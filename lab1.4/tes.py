def bitwise_nimply( a,b):
    return ~b

def is_all_ones(n):
    # Проверяем, состоит ли число только из единиц
    if n == 0:
        return False
    # Создаем маску, состоящую из единиц, с тем же количеством битов, что и n
    mask = (1 << n.bit_length()) - 1
    return n == mask

# Пример использования
a = 0b1100  # 12 в десятичной системе
b = 0b1111  # 10 в десятичной системе
print(a)
print(b)
result = bitwise_nimply(a, b)
print(f"Результат побитовой обратной импликации: {bin(result)}")

if is_all_ones(result):
    print("Результат состоит только из единиц.")
else:
    print("Результат не состоит только из единиц.")