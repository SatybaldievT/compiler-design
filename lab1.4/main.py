import re
import Token as tk
import copy
from Token import DomainTag
class Graph:
    def __init__(self):
        self.graph = {}
        self.final = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = set()

    def add_edge(self, vertex1, vertex2,regex):
        if vertex1 not in self.graph:
            self.add_vertex(vertex1)
        if vertex2 not in self.graph:
            self.add_vertex(vertex2)
        self.graph[vertex1].add((vertex2,regex))
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

            for neighbor, regex in self.graph.get(current_vertex, []):
                
                match = re.match(regex, pos.str)
                if match:
                    matched_length = match.end()
                    _pos = copy.copy(pos)
                    _pos+=1
                    
                    if matched_length > 0 and dfs(neighbor, _pos):
                        return True
            if current_vertex in self.final:
                            final_vertices_reached.append((current_vertex, pos))
            return False

        dfs(start_vertex, pos)
        if len(final_vertices_reached) == 0 :
             fragm = tk.Fragment(prev_pos,prev_pos)
             prev_pos+=1
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
   ("Start","WhiteSpace", r"[\s\t\n\r]"),
   ("WhiteSpace","WhiteSpace", r"[\s\t\n\r]"),
   ("Start","Number", r'[0-9]'),
   ("Number","Number", r'[0-9]'),
   ("Start","IDENT", r'(?![IF])[A-Za-z]'),
   ("Start","I", r'I'),
   ("Start","F", r'F'),
   ("I","n", r'n'),
   ("I","IDENT", r'(?![IFn])[A-Za-z0-9]'),
   ("n","t", r't'),
   ("n","IDENT", r'(?![IFt])[A-Za-z0-9]'),
   ("t","e", r'e'),
   ("t","IDENT", r'(?![IFe])[A-Za-z0-9]'),
   ("e","g", r'g'),
   ("e","IDENT", r'(?![IFg])[A-Za-z0-9]'),
   ("g","e1", r'e'),
   ("g","IDENT", r'(?![IFe])[A-Za-z0-9]'),
   ("e1","Integer", r'r'),
   ("e1","IDENT", r'(?![IFr])[A-Za-z0-9]'),
   ("Integer","IDENT", r'(?![IF])[A-Za-z0-9]'),
   ("F", "l", r'l'),
   ("F", "IDENT", r'(?![IFl])[A-Za-z0-9]'),
   ("l", "o", r'o'),
   ("l", "IDENT", r'(?![IFo])[A-Za-z0-9]'),
   ("o", "a", r'a'),
   ("o", "IDENT", r'(?![IFa])[A-Za-z0-9]'),
   ("a", "Float", r't'),
   ("a", "IDENT", r'(?![IFt])[A-Za-z0-9]'),
   ("Float", "IDENT",r'(?![IF])[A-Za-z0-9]') , 
   ("IDENT","IDENT",r'(?![IF])[A-Za-z0-9]'),
   ("Start","{", r'{'),
   ("{","-", r'-'),
   ("-","-", r'[^-]'),
   ("-","_", r'-'),
   ("_","_", r'-'),
    ("_","-", r'[^-}]'),
   ("_","Comment", r'}'),
   ("Start",":", r':'),
   (":","::", r':'),
   ("Start","-.>", r'-'),
   ("-.>","->", r'>'),
   ("Start","=", r'=')]
    final = [
    ("WhiteSpace",DomainTag.WhiteSpace),
    ("Comment",DomainTag.COMMENT),
    ("I",DomainTag.IDENT),
    ("n",DomainTag.IDENT),
    ("t",DomainTag.IDENT),
    ("e",DomainTag.IDENT),
    ("g",DomainTag.IDENT),
    ("e1",DomainTag.IDENT),
    ("Integer",DomainTag.Integer),
    ("F",DomainTag.IDENT),
    ("l",DomainTag.IDENT),
    ("o",DomainTag.IDENT),
    ("a",DomainTag.IDENT),
    ("Float",DomainTag.Float),
    ("IDENT",DomainTag.IDENT),
    ("Number",DomainTag.NUMBER),
    ("::",DomainTag.DOUBLE_COLON),
    ("->",DomainTag.ARROW),
    ("=",DomainTag.EQUALS),]
    list(map(lambda args: g.add_edge(*args), edges))
    list(map(lambda args: g.add_final_vertices(*args), final))
    return g    
g = graph_init()
print(g)
# input_string = ""
# with open('text.txt', 'r', encoding='utf-8') as file:
#     # Читаем содержимое файла в строку
#     input_string = file.read()

# lex = Lexer(g,input_string)

# token = lex.next_token()
# print(token) 
# while (token.tag != DomainTag.END_OF_PROGRAM):
#     token = lex.next_token()
#     print(token) 