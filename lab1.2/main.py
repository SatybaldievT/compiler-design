import re
from typing import List, Optional

# Определение структуры токена
class Token:
    def __init__(self, tag: str, line: int, column: int, value: str):
        self.tag = tag
        self.line = line
        self.column = column
        self.value = value

    def __repr__(self):
        return f"{self.tag} ({self.line}, {self.column}): {self.value}"

# Лексические домены
DOMAINS = [
    ("COMMENT", re.compile(r"//.*")),  # Комментарии
    ("KEYWORD", re.compile(r"/(while|do|end)/")),  # Ключевые слова
    ("IDENT", re.compile(r"/[^/]+/")),  # Идентификаторы
    ("WHITESPACE", re.compile(r"(\s|\t)+")),  # Пробельные символы
]

class LexicalAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.line = 1
        self.column = 1
        self.buffer = ""
        self.current_pos = 0

    def read_file(self) -> str:
        """Чтение всего файла в буфер."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.read()

    def next_token(self) -> Optional[Token]:
        """Поиск следующего токена."""
        while self.current_pos < len(self.buffer):
            for domain_name, pattern in DOMAINS:
                regex = re.compile(pattern.pattern)
                match = regex.match(self.buffer, self.current_pos)
                if match:
                    value = match.group(0)
                    start_pos = match.start()
                    end_pos = match.end()

                    # Пропускаем пробельные символы
                    if domain_name == "WHITESPACE":
                        self.current_pos = end_pos   
                        self.column += len(value)
                        if "\n" in value:
                            self.line += value.count("\n")
                            self.column = 1 + len(value.split("\n")[-1])
                        return self.next_token()
                        

                    # Создаем токен
                    token = Token(
                        tag=domain_name,
                        line=self.line,
                        column=self.column + start_pos - self.current_pos,
                        value=value,
                    )

                    # Обновляем позицию
                    self.current_pos = end_pos  
                    self.column += end_pos - start_pos
                    if "\n" in value:
                        self.line += value.count("\n")
                        self.column = 1 + len(value.split("\n")[-1])

                    return token

            # Если ни один домен не подошел, это ошибка
            error_token = Token(
                tag="ERROR",
                line=self.line,
                column=self.column,
                value=f"syntax error",
            )
            self.current_pos += 1
            self.column += 1
            return error_token

        return None  # Конец файла

    def analyzeFullError(self) -> List[Token]:
        """Запуск лексического анализа."""
        self.buffer = self.read_file()
        tokens = []
        while True:
            token = self.next_token()
            if token is None:
                break
            tokens.append(token)
        return tokens
    def analyze(self) -> List[Token]:
        """Запуск лексического анализа."""
        self.buffer = self.read_file()
        tokens = []
        prev_token_was_error = False  # Флаг для отслеживания предыдущего токена

        while True:
            token = self.next_token()
            if token is None:
                break

            # Если текущий токен — ошибка и предыдущий токен тоже был ошибкой, пропускаем
            if token.tag == "ERROR" and prev_token_was_error:
                continue

            # Добавляем токен в список
            tokens.append(token)

            # Обновляем флаг
            prev_token_was_error = token.tag == "ERROR"

        return tokens


# Пример использования
if __name__ == "__main__":
    analyzer = LexicalAnalyzer("./input.txt")
    tokens = analyzer.analyze()
    for token in tokens:
        print(token)