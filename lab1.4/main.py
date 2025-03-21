from enum import Enum
import re
import Token as tk
import copy
from Token import DomainTag
class CLS(Enum):
    CHR_SPEC = 0          # строчные символы без I n t e g r F l o a t : - > 
    NUM = 1               # Число 
    I = 3                # Символ 'I'
    n = 4                # Символ 'n'
    t = 5                # Символ 't'
    e = 6                # Символ 'e'
    g = 7                # Символ 'g'
    r = 8                # Символ 'r'
    F = 9                # Символ 'F'
    l = 10               # Символ 'l'
    a = 11               # Символ 'a'
    o = 12               # Символ 'o'
    COLON = 13           # Символ ':'
    GT = 14              # Символ '>'
    MIN = 15             # Символ '-'
    OAS = 16             # Символ '{'
    CAS = 17             # Символ '}'
    EQ = 18              # Символ '='  
    EOF = 99             # Конец файла (End of File)
    WS = 100             # Пробельный символ (Whitespace)
    Other = 101          # другие символы 
# Создание словаря
char_to_cls = {
    'I': CLS.I,
    'n': CLS.n,
    't': CLS.t,
    'e': CLS.e,
    'g': CLS.g,
    'r': CLS.r,
    'F': CLS.F,
    'l': CLS.l,
    'a': CLS.a,
    'o': CLS.o,
    ':': CLS.COLON,
    '>': CLS.GT,
    '-': CLS.MIN,
    '{': CLS.OAS,
    '}': CLS.CAS,
    '=': CLS.EQ
}
def getCLS(x: str) -> CLS:
    if len(x) != 1:
        raise ValueError("Input must be a single character")
    match x :
        case char_to_cls[x]:
            return char_to_cls[x]
        case x.isdigit():
            return CLS.NUM
        case x.isspace():
            return CLS.WS
        case x.isalpha():
            return CLS.CHR_SPEC
        case _:
            return CLS.Other  
        
class Graph:
    def __init__(self):
        self.graph = {}
        self.final = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = set()

    def add_edge(self, vertex1, vertex2, regex):
        if vertex1 not in self.graph:
            self.add_vertex(vertex1)
        if vertex2 not in self.graph:
            self.add_vertex(vertex2)
        
        if isinstance(regex, list):
            for r in regex:
                self.graph[vertex1].add((vertex2, r))
        else:
            self.graph[vertex1].add((vertex2, regex))
    def add_final_vertices(self,vertex,domain_name):
        if vertex not in self.graph:
            self.add_vertex(vertex)
        self.final[vertex] = domain_name
    def get_vertices(self):
        return list(self.graph.keys())
    

    def get_edges(self):
        edges = []
        for vertex in self.graph:
            for adjacent_vertex in self.graph[vertex]:
                if (adjacent_vertex, vertex) not in edges:  # Чтобы избежать дублирования в неориентированном графе
                    edges.append((vertex, adjacent_vertex))
        return edges

    def __str__(self):
        dot =  "digraph G {\n"
        for vertex in self.graph:
            if vertex in self.final:
                dot += f'    "{vertex}" [shape="doubleoctagon"];\n'
            else :
                dot += f'    "{vertex}";\n'

            
        for vertex, adjacents in self.graph.items():
            for adj,regex in adjacents:
                  # Для неориентированного графа избегаем дублирования рёбер
                dot += f'    "{vertex}" -> "{adj}" [label="{regex}"];\n' 
        dot += "}"
        return dot
    def csacademy_format(self):
        dot = ""
        
        # Добавляем вершины
        for vertex in self.graph:
            if vertex in self.final:
                dot += f'"{vertex}_finish"\n'
            else:
                dot += f'"{vertex}"\n'
        
        # Добавляем рёбра
        for vertex, adjacents in self.graph.items():
            for adj, regex in adjacents:
                # Определяем имена вершин с учётом приставки _finish
                start_vertex = f'"{vertex}_finish"' if vertex in self.final else f'"{vertex}"'
                end_vertex = f'"{adj}_finish"' if adj in self.final else f'"{adj}"'
                
                # Добавляем ребро с меткой
                dot += f'{start_vertex} {end_vertex} "{regex}"\n'
        
        return dot
    def traverse(self, start_vertex, pos):
        final_vertices_reached = []
        prev_pos = copy.copy(pos)
        
        if pos.cp < 0:
            fragm = tk.Fragment(pos,pos)
            return (tk.Token(DomainTag.END_OF_PROGRAM,"",fragm), pos) 
        def dfs(current_vertex, pos):
            if pos.cp < 0:
                if current_vertex in self.final:
                    final_vertices_reached.append((current_vertex, pos))
                
                return True  # Строка полностью пройдена
            
            # print(current_vertex , " \" ",pos.str,"\"",end= " ")
            
            for neighbor, regex in self.graph.get(current_vertex, []):
                _pos = copy.copy(pos)
                _pos+=1

                if getCLS(pos.str)==regex  and dfs(neighbor, _pos):
                    if current_vertex in self.final:
                        final_vertices_reached.append((current_vertex, pos))
                    return True
            if current_vertex in self.final:
                final_vertices_reached.append((current_vertex, pos))
            return False

        dfs(start_vertex, pos)
        if len(final_vertices_reached) == 0 :
             ps = copy.copy(prev_pos)
             prev_pos+=1
             fragm = tk.Fragment(ps,prev_pos)
             
             return (tk.Token(DomainTag.ERROR,fragm.str,fragm),prev_pos)
        
        vertex,pos =final_vertices_reached[0]
        fragm = tk.Fragment(prev_pos,pos)
        
        return (tk.Token(self.final[vertex],fragm.str,fragm), pos)
# Пример использования
class Lexer:
    def __init__(self,graph,text):
        self.graph = graph
        self.text = text
        self.pos = tk.Position(text)
    def next_token(self):
        Token,_pos = g.traverse("Start", self.pos )
        # print("first token=",Token)
      
        while Token.tag ==  DomainTag.WhiteSpace : 
            Token,_pos = g.traverse("Start", _pos)
            
        self.pos = _pos 
        return Token
def graph_init():
    g = Graph()
    edges = [
   ("Start","WhiteSpace", CLS.WS),
   ("WhiteSpace","WhiteSpace", CLS.WS),
   ("Start","Number", CLS.NUM),
   ("Number","Number", CLS.NUM),
   ("Start","IDENT",[CLS.CHR_SPEC, CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.l,CLS.o,CLS.a]),
   ("Start","I", CLS.I),
   ("Start","F",CLS.F),
   ("I","n", CLS.n),
   ("I","IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("n","t", CLS.t),
   ("n","IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("t","e", CLS.e),
   ("t","IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("e","g", CLS.g),
   ("e","IDENT",[CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("g","e1", CLS.e),
   ("g","IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("e1","Integer", CLS.r),
   ("e1","IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("Integer","IDENT",[CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("F", "l", CLS.l),
   ("F", "IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("l", "o", CLS.o),
   ("l", "IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.a]),
   ("o", "a", CLS.a),
   ("o", "IDENT",[CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o]),
   ("a", "Float", CLS.t),
   ("a", "IDENT", [CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("Float", "IDENT",[CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]) , 
   ("IDENT","IDENT",[CLS.CHR_SPEC,CLS.NUM,CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,CLS.F,CLS.l,CLS.o,CLS.a]),
   ("Start","{", CLS.OAS),
   ("{","-", CLS.MIN),
   ("-","-", [CLS.CHR_SPEC,CLS.NUM,
              CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,
              CLS.F,CLS.l,CLS.o,CLS.a,
              CLS.Other,CLS.COLON,CLS.WS,CLS.GT,CLS.OAS,CLS.CAS]),
    ("_","-", [CLS.CHR_SPEC,CLS.NUM,
              CLS.I,CLS.n,CLS.t,CLS.e,CLS.g,CLS.r,
              CLS.F,CLS.l,CLS.o,CLS.a,
              CLS.Other,CLS.COLON,CLS.WS,CLS.GT,CLS.OAS]),
    ("-","_", CLS.MIN),
    ("_","_", CLS.MIN),
    ("_","Comment", CLS.CAS),
    ("Start",":.:",CLS.COLON) ,
    (":.:","::",CLS.COLON) ,
    
    ("Start","-.>",CLS.MIN) ,
    ("-.>","->",CLS.GT) ,
    
    ("Start","=",CLS.EQ) ,
   ]
    final = [
    ("WhiteSpace",DomainTag.WhiteSpace),
    ("Comment",DomainTag.COMMENT),
    ("I",DomainTag.IDENT),
    ("n",DomainTag.IDENT),
    ("t",DomainTag.IDENT),
    ("e",DomainTag.IDENT),
    ("g",DomainTag.IDENT),
    ("e1",DomainTag.IDENT),
    ("Integer",DomainTag.KeyWord),
    ("F",DomainTag.IDENT),
    ("l",DomainTag.IDENT),
    ("o",DomainTag.IDENT),
    ("a",DomainTag.IDENT),
    ("Float",DomainTag.KeyWord),
    ("IDENT",DomainTag.IDENT),
    ("Number",DomainTag.NUMBER),
    ("::",DomainTag.OP),
    ("->",DomainTag.OP),
    ("=",DomainTag.OP),]
    list(map(lambda args: g.add_edge(*args), edges))
    list(map(lambda args: g.add_final_vertices(*args), final))
    return g    
g = graph_init()
# print(g)
input_string = ""
with open('text.txt', 'r', encoding='utf-8') as file:
    # Читаем содержимое файла в строку
    input_string = file.read()

lex = Lexer(g,input_string)

token = lex.next_token()
print(token) 
while (token.tag != DomainTag.END_OF_PROGRAM):
    token = lex.next_token()
    print(token)
token = lex.next_token()
print(token) 