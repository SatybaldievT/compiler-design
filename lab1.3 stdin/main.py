from abc import abstractmethod
import copy
import sys
import unicodedata
from enum import Enum
class Position:
    def __init__(self, stdin):
        self.stdin = stdin
        self.line = 1
        self.pos = 1
        self.prev = self.stdin.read(1)
        self.next = self.stdin.read(1)
        self.prev1 = None
        self.prev2 = None 
    def update_text(self, new_text):
        """
        Обновляет текст и сбрасывает индекс, но сохраняет текущие значения line и pos.
        """
        self.text = new_text
        self.index = 0  # Сбрасываем индекс
    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, value):
        self._line = value

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

   

    @property 
    def cp(self):
        if not self.prev:
            return -1
        return ord(self.prev)

    @property
    def uc(self):
        if self.index == len(self.text):
            return unicodedata.category(' ')
        return unicodedata.category(self.text[self.index])

    @property
    def is_white_space(self):
        return self.prev  and self.prev.isspace()

    @property
    def is_letter(self):
        return self.index != len(self.text) and self.text[self.index].isalpha()

    @property
    def is_letter_or_digit(self):
        return self.index != len(self.text) and self.text[self.index].isalnum()

    @property
    def is_decimal_digit(self):
        return self.index != len(self.text) and self.text[self.index].isdigit()

    @property
    def is_new_line(self):
        if not self.prev:
            return True
        if self.prev == '\r' and self.next:
            return self.next == '\n'
        return self.prev == '\n'

    def __iadd__(self, other):
        self.prev2 = self.prev1
        self.prev1 = self.prev
        self.prev = self.next
        if self.prev:
            self.next = self.stdin.read(1)
            
            if self.is_new_line:
                if self.prev == '\r':
                    self.prev = self.next
                    self.next = self.stdin.read(1)
                self.line += 1
                self.pos = 1
            else:
                if unicodedata.category(self.prev) == 'Cs':
                    self.prev = self.next
                    self.next = self.stdin.read(1)
                self.pos += 1
            
        return self
    def __isub__(self, other):
        raise 

    def __str__(self):
        return f"({self.line}, {self.pos})"

class Fragment:
    def __init__(self, starting, following):
        self._starting = copy.copy(starting)  # Копируем starting
        self._following = copy.copy(following)  # Копируем following

    @property
    def starting(self):
        return self._starting

    @property
    def following(self):
        return self._following

    def __str__(self):
        return f"{self.starting}-{self.following}"
class Message:
    def __init__(self, is_error, text):
        self._is_error = is_error
        self._text = text

    @property
    def is_error(self):
        return self._is_error

    @property
    def text(self):
        return self._text

    def __str__(self):
        return f"{'Error' if self.is_error else 'Message'}: {self.text}"


class DomainTag(Enum):
    IDENT = 0          # Идентификатор
    NUMBER = 1         # Число
    CHAR = 2           # Символ
    LPAREN = 3         # Спецсимвол '('
    RPAREN = 4         # Спецсимвол ')'
    PLUS = 5           # Спецсимвол '+'
    MINUS = 6          # Спецсимвол '-'
    MULTIPLY = 7       # Спецсимвол '*'
    DIVIDE = 8         # Спецсимвол '/'
    END_OF_PROGRAM = 9 # Конец программы
    STRING = 10         # Строка
    COMMENT = 11 
class Token():
    def __init__(self, tag, starting, following):
        self._tag = tag
        self._coords = Fragment(starting, following)

    @property
    def tag(self):
        return self._tag

    @property
    def coords(self):
        return self._coords
    @abstractmethod
    def get_value(self):
        pass
    
    def __str__(self):
        return f"{self.tag.name} {self.coords}: {self.get_value()}"


# Класс IdentToken
class IdentToken(Token):
    def __init__(self, code, starting, following):
        super().__init__(DomainTag.IDENT, starting, following)
        self._code = code

    @property
    def code(self):
        return self._code

    def get_value(self):
        return f"Code={self.code}"

# Класс NumberToken
class NumberToken(Token):
    def __init__(self, value, starting, following):
        super().__init__(DomainTag.NUMBER, starting, following)
        self._value = value

    @property
    def value(self):
        return self._value

    def get_value(self):
        return f"Value={self.value}"

# Класс CharToken
class CharToken(Token):
    def __init__(self, code_point, starting, following):
        super().__init__(DomainTag.CHAR, starting, following)
        self._code_point = code_point

    @property
    def code_point(self):
        return self._code_point

    def get_value(self):
        return f"CodePoint={self.code_point}"
class StringToken(Token):
    def __init__(self, value, starting, following):
        super().__init__(DomainTag.STRING, starting, following)
        self._value = value

    @property
    def value(self):
        return self._value

    def get_value(self):
        return f"Value={self.value}"
class CommentToken(Token):
    def __init__(self, value, starting, following):
        super().__init__(DomainTag.COMMENT, starting, following)
        self._value = value

    @property
    def value(self):
        return self._value

    def get_value(self):
        return f"Value={self.value}"
class SpecToken(Token):
    def __init__(self, tag, starting, following):
        # Проверка, что tag является допустимым для SpecToken
        assert tag in {
            DomainTag.LPAREN,
            DomainTag.RPAREN,
            DomainTag.PLUS,
            DomainTag.MINUS,
            DomainTag.MULTIPLY,
            DomainTag.DIVIDE,
            DomainTag.END_OF_PROGRAM
        }, f"Invalid tag for SpecToken: {tag}"
        
        super().__init__(tag, starting, following)
#dsfdsf
class Lexer:
    def __init__(self, stdin):
        self.cur = Position(stdin)  # Текущая позиция в тексте
        self.messages = []
        self.comments = []
        self.have_open_comment_error  = False
    def next_token(self):

        while True:
            try:
                token = self.next_token_raw()
                # Создаем объект Message для токена
                #token_message = Message(is_error=False, text=f"Token: {token}")
                # Добавляем сообщение в список
                if token.tag == DomainTag.END_OF_PROGRAM:
                    return token
                else:
                    if token.__class__.__name__ == "CommentToken": 
                        self.comments.append(token)
                    else:
                        return token
    
            except ValueError as e:
                # Создаем объект Message для ошибки
                error_message = Message(is_error=True, text=str(e))
                self.messages.append(error_message)  # Добавляем сообщение в список
                # Пропускаем текущий символ и продолжаем
                if self.cur.cp != -1:
                    self.cur += 1  # Перемещаем позицию вперед
                continue  # Продолжаем цикл

    def update_text(self, new_text):
        """
        Обновляет текст и сбрасывает индекс, но сохраняет текущие значения line и pos.
        """
        self.cur.update_text(new_text) # Сбрасываем индекс
    def _skip_comment(self,start):
        """
        Пропускает комментарий, начинающийся на (* и заканчивающийся на *).
        Возвращает содержимое комментария.
        """
        self.cur += 1  # Пропускаем '(*'
        self.cur += 1
        content = ""
        while self.cur.cp != -1:
            
            if chr(self.cur.cp) == '(' :
                self.cur += 1
                if chr(self.cur.cp) == '*':
                    self.cur += 1
                    raise ValueError("Nested comments are not allowed")
                else :
                    content += '('
                    content += chr(self.cur.cp)
            if chr(self.cur.cp) == '*':
                self.cur += 1
                if chr(self.cur.cp) == ')':
                    self.cur += 1
                    return CommentToken(content, start, self.cur)
                  # Пропускаем '*)'
                else:
                    content += '*'
                    content += chr(self.cur.cp)
                
            content += chr(self.cur.cp)
            self.cur += 1
        raise ValueError("Unclosed comment")

    def _read_number(self, start):
        """Читает число и возвращает NumberToken."""
        value = 0
        while self.cur.cp != -1 and chr(self.cur.cp).isdigit():
            digit = int(chr(self.cur.cp))
            value = value * 10 + digit
            self.cur += 1
            # Проверка на переполнение (если число слишком большое)
            if value > sys.maxsize:
                raise ValueError(f"Number too large at {start}")
        return NumberToken(value, start, self.cur)

    def _read_string(self, start):
        """Читает строку и возвращает StringToken."""
        self.cur += 1  # Пропускаем '{'
        value = ""
        while self.cur.cp != -1 and chr(self.cur.cp) != '}':
            if self.cur.cp == ord('\n'):
                raise ValueError(f"String crosses line boundary at {start}")
            if chr(self.cur.cp) == '#':
                # Обработка escape-последовательностей
                self.cur += 1
                if self.cur.cp == -1:
                    raise ValueError(f"Unfinished escape sequence at {start}")
                match chr(self.cur.cp):
                    case '{':
                        value += '{'
                    case '}':
                        value += '}'
                    case '#':
                        value += '#'
                    case _ if chr(self.cur.cp).lower() in '0123456789abcdef':
                        # Обработка #hh (шестнадцатеричный код символа)
                        hex_digits = chr(self.cur.cp)
                        self.cur += 1
                        if self.cur.cp == -1 or chr(self.cur.cp).lower() not in '0123456789abcdef':
                            raise ValueError(f"Invalid hex escape sequence at {start}")
                        hex_digits += chr(self.cur.cp)
                        try:
                            value += chr(int(hex_digits, 16))
                        except ValueError:
                            raise ValueError(f"Invalid hex escape sequence at {start}")
                    case _:
                        raise ValueError(f"Invalid escape sequence at {start}")
            else:
                value += chr(self.cur.cp)
            self.cur += 1
        if self.cur.cp == -1:
            raise ValueError(f"Unclosed string at {start}")
        self.cur += 1  # Пропускаем '}'
        return StringToken(value, start, self.cur)

    def next_token_raw(self):
        "the comment"
        while self.cur.cp != -1:  # Пока не достигнут конец текста
            # Пропускаем пробелы
            while self.cur.is_white_space:
                self.cur += 1

            start = copy.copy(self.cur)  # Начальная позиция токена
            

            if self.cur.cp == -1:
                break

            # Обработка комментариев
            if self.have_open_comment_error:
                return self._skip_comment(start)
            # Обработка символов с использованием match
            match chr(self.cur.cp):
                case '{':
                    return self._read_string(start)
                case '(':
                    _cur = copy.copy(self.cur)
                    _cur+=1
                    if  chr(_cur.cp) == '*':
                        return self._skip_comment(start)
                    self.cur += 1
                    return SpecToken(DomainTag.LPAREN, start, self.cur)
                case ')':
                    self.cur += 1
                    return SpecToken(DomainTag.RPAREN, start, self.cur)
                case '+':
                    self.cur += 1
                    return SpecToken(DomainTag.PLUS, start, self.cur)
                case '-':
                    self.cur += 1
                    return SpecToken(DomainTag.MINUS, start, self.cur)
                case '*':
                    self.cur += 1
                    return SpecToken(DomainTag.MULTIPLY, start, self.cur)
                case '/':
                    self.cur += 1
                    return SpecToken(DomainTag.DIVIDE, start, self.cur)
                case _ if chr(self.cur.cp).isdigit():  # Если текущий символ — цифра
                    return self._read_number(start)
                case _:
                    # Если символ не распознан, выбрасываем исключение
                    raise ValueError(f"Unexpected character: {chr(self.cur.cp)} at {start}")

        # Если достигнут конец текста, возвращаем токен конца программы
        return SpecToken(DomainTag.END_OF_PROGRAM, self.cur, self.cur)
text = """
( 123213  + / * )
{asddsd } { sdad }
ds
(* dsfsd *)
"""
text2 = "(* (* Comment *)"

# Инициализация текущей позиции
lex = Lexer(sys.stdin)
token = lex.next_token()

while token.tag != DomainTag.END_OF_PROGRAM:
    print(f"Token: {token}")
    token = lex.next_token()
for error_message in lex.messages:
    print(f"Error_message: {error_message}")

for comment in lex.comments:
    print(f"Comment: {comment}")
# Вывод:
# LPAREN (1, 1)-(1, 2)
# PLUS (1, 3)-(1, 4)
# MULTIPLY (1, 5)-(1, 6)
# RPAREN (1, 7)-(1, 8)
# END_OF_PROGRAM (1, 8)-(1, 8)