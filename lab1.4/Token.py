from abc import abstractmethod
import copy
import sys
import unicodedata
from enum import Enum
class Position:
    def __init__(self, text):
        self.text = text
        self.line = 1
        self.pos = 1
        self.index = 0
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
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value
    
    @property 
    def cp(self):
        if self.index == len(self.text):
            return -1
        return ord(self.text[self.index])
    @property 
    def str(self):
        if self.index == len(self.text):
            return ""
        return self.text[self.index:self.index+1]
    @property
    def uc(self):
        if self.index == len(self.text):
            return unicodedata.category(' ')
        return unicodedata.category(self.text[self.index])

    @property
    def is_white_space(self):
        return self.index != len(self.text) and self.text[self.index].isspace()

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
        if self.index == len(self.text):
            return True
        if self.text[self.index] == '\r' and self.index + 1 < len(self.text):
            return self.text[self.index + 1] == '\n'
        return self.text[self.index] == '\n'

    def __iadd__(self, other):
        if self.index < len(self.text):
            if self.is_new_line:
                if self.text[self.index] == '\r':
                    self.index += 1
                self.line += 1
                self.pos = 1
            else:
                if unicodedata.category(self.text[self.index]) == 'Cs':
                    self.index += 1
                self.pos += 1
            self.index += 1
        return self
    def __isub__(self, other):
        """Перемещает позицию назад на `other` символов."""
        for _ in range(other):
            if self.index <= 0:
                break  # Нельзя уйти ниже нулевого индекса
            self.index -= 1  # Перемещаемся на один символ назад

            # Если текущий символ — это символ новой строки, обновляем line и pos
            if self.index > 0 and self.text[self.index - 1] == '\n':
                self.line -= 1
                # Вычисляем pos как длину строки до текущего символа
                self.pos = self.text.rfind('\n', 0, self.index - 1)
                if self.pos == -1:
                    self.pos = self.index
                else:
                    self.pos = self.index - self.pos - 1
            elif self.index > 0 and self.text[self.index - 1] == '\r':
                # Обработка случая с \r\n
                if self.index > 1 and self.text[self.index - 2] == '\n':
                    self.line -= 1
                    self.pos = self.text.rfind('\n', 0, self.index - 2)
                    if self.pos == -1:
                        self.pos = self.index - 1
                    else:
                        self.pos = self.index - self.pos - 2
                else:
                    self.line -= 1
                    self.pos = 1
            else:
                self.pos -= 1
        return self

    def __str__(self):
        return f"({self.line}, {self.pos})"

    def __lt__(self, other):
        return self.index < other.index

    def __eq__(self, other):
        return self.index == other.index

    def __le__(self, other):
        return self.index <= other.index

    def __gt__(self, other):
        return self.index > other.index

    def __ge__(self, other):
        return self.index >= other.index

    def __ne__(self, other):
        return self.index != other.index
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
    @property
    def str(self):
        return self._starting.text[self._starting.index : self._following.index]
    
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
    COMMENT = 2 
    Integer = 3
    Float = 4
    DOUBLE_COLON = 5
    EQUALS = 6
    ARROW = 7
    ERROR = 98
    END_OF_PROGRAM = 99
    WhiteSpace = 100
  
class Token():
    def __init__(self, tag,value, starting, following):
        self._tag = tag
        self._value = value
        self._coords = Fragment(starting, following)
    def __init__(self, tag,value, coords):
        self._tag = tag
        self._value = value
        self._coords = coords
    @property
    def tag(self):
        return self._tag

    @property
    def coords(self):
        return self._coords
    @property
    def get_value(self):
        return self._value
    
    def __str__(self):
        return f"{self.tag.name} {self.coords}: {self.get_value}"
