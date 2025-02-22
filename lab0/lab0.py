class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()
        self.articles_obj = {}
        # Список специальных слов, которые не могут быть идентификаторами
        self.reserved_words = {'if', 'else', 'define', 'end', 'endif', 'integer'}

    def next_token(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)
        else:
            self.current_token = None

    def parse(self):
        return self.program()

    def program(self):
        try:
            self.articles()
            body = self.body()
            return (self.articles_obj, body)
        except SyntaxError:
            return None

    def articles(self):
        if self.current_token == 'define':
            self.article()
            self.articles()
            #return ('Articles', article, articles)
        #else:
            #return ('Articles',)  # Empty articles

    def article(self):
        if self.current_token != 'define':
            raise SyntaxError("Expected 'define'")
        self.next_token()

        if not self.is_word(self.current_token):
            raise SyntaxError(f"Expected a word after 'define', but got '{self.current_token}'")
        word = self.current_token
        self.next_token()

        body = self.body()

        if self.current_token != 'end':
            raise SyntaxError("Expected 'end' after article body")
        self.next_token()
        self.articles_obj[word]= body; 
        #return ('Article', word, body)

    def body(self):
        if self.current_token == 'if':
            self.next_token()
            body_if = self.body()
            else_part = self.elsepart()
            if self.current_token != 'endif':
                raise SyntaxError("Expected 'endif' after if-body")
            self.next_token()
            body_after = self.body()
            return ('Body', 'if', body_if, else_part, 'endif', body_after)
        elif self.is_number(self.current_token) :
            self.next_token()
            body_after = self.body()
            return ('Body', 'integer', body_after)
        elif self.is_word(self.current_token):
            word = self.current_token
            self.next_token()
            body_after = self.body()
            return ('Body', word, body_after)
        else:
            return ('Body',)  # Empty body

    def elsepart(self):
        if self.current_token == 'else':
            self.next_token()
            body = self.body()
            return ('ElsePart', 'else', body)
        else:
            return ('ElsePart',)  # Empty else part

    def is_word(self, token):
        # Проверяем, что токен является допустимым идентификатором и не является специальным словом
        return (
            token
            and isinstance(token, str)
            and token not in self.reserved_words
        )

    def is_word_define(self, token):
        # Проверяем, что токен является допустимым идентификатором и не является специальным словом
        return (
            token
            and isinstance(token, str)
            and token.isidentifier()
            and token not in self.reserved_words
        )

    def is_number(self, token):
        return (
            token
            and token.isnumeric()
        )

def parse(text):
    tokens = text.split()

    # Парсинг
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)

# Пример использования
input_text = """
define -- 1 - end
          define =0? dup 0 = end
          define =1? dup 1 = end
          define factorial
              =0? if drop 1 exit endif
              =1? if drop 1 exit endif
              dup --
              factorial
              *
          end
          0 factorial
          1 factorial
          2 factorial
          3 factorial
          4 factorial
"""
parse(input_text)
# Токенизация входных данных
