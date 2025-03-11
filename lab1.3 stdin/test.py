
import sys

print("Введите текст (Ctrl+Z для завершения на Windows, Ctrl+D на Linux/macOS):")

while True:
    data = sys.stdin.read(1)  # Читаем по одному символу
    if not data:  # Если data == "", значит, достигнут конец ввода
        print("Конец ввода (EOF).")
        break
    if data == '\n':
        print("\nКонец n")
    print(f"Прочитан символ: {data}", end="")