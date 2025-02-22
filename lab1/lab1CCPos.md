% Лабораторная работа № 1.1. Раскрутка самоприменимого компилятора
% 12 февраля 2025 г.
% Талгат Сатыбалдиев, ИУ9-62Б

# Цель работы
Целью данной работы является ознакомление с раскруткой самоприменимых компиляторов на примере модельного 
компилятора.

# Индивидуальный вариант
Компилятор BeRo. Разрешить использовать знак .. вместо ключевого слова to при записи цикла for. При этом 
использование слова to не запрещается.

# Реализация

Различие между файлами `pcom.pas` и `pcom2.pas`:

```diff
Сравнение файлов btpc.pas и BTPC2.PAS
***** btpc.pas
  SymTO:begin
   Write('"to" expected');
  end;
***** BTPC2.PAS
  SymTO:begin
   Write('".." expected');
  end;
*****

***** btpc.pas
  129:begin
   Write('"TO" or "DOWNTO" expected');
  end;
***** BTPC2.PAS
  129:begin
   Write('".." or "DOWNTO" expected');
  end;
*****

***** btpc.pas
    Expect(SymTO);
   end else if CurrentSymbol=sYMdownto then begin
***** BTPC2.PAS
    Expect(SymTO);
   end else if CurrentSymbol=TokColon then begin
    Expect(TokColon);
   end else if CurrentSymbol=sYMdownto then begin
*****

```

Различие между файлами `pcom2.pas` и `pcom3.pas`:

```diff
Сравнение файлов btpc2.pas и BTPC3.PAS
***** btpc2.pas
begin
 for i:=1 to OutputCodeDataSize do begin
  write(OutputCodeData[i]);
***** BTPC3.PAS
begin
 for i:=1 .. OutputCodeDataSize do begin
  write(OutputCodeData[i]);
*****

***** btpc2.pas
begin
 for i:=1 to 20 do begin
  EmitChar(s[i]);
***** BTPC3.PAS
begin
 for i:=1 .. 20 do begin
  EmitChar(s[i]);
*****

***** btpc2.pas
 { Patch jumps + calls }
 for Index:=1 to CountJumps do begin
  Value:=JumpTable[Index];
***** BTPC3.PAS
 { Patch jumps + calls }
 for Index:=1 .. CountJumps do begin
  Value:=JumpTable[Index];
*****


C:\Users\Admi\Desktop\btpc-windows>fc btpc.pas btpc2.pas
Сравнение файлов btpc.pas и BTPC2.PAS
***** btpc.pas
  SymTO:begin
   Write('"to" expected');
  end;
***** BTPC2.PAS
  SymTO:begin
   Write('"to" or ".." expected');
  end;
*****

***** btpc.pas
  129:begin
   Write('"TO" or "DOWNTO" expected');
  end;
***** BTPC2.PAS
  129:begin
   Write('"TO" or ".." or "DOWNTO" expected');
  end;
*****

***** btpc.pas
    Expect(SymTO);
   end else if CurrentSymbol=sYMdownto then begin
***** BTPC2.PAS
    Expect(SymTO);
   end else if CurrentSymbol=TokColon then begin
    Expect(TokColon);
   end else if CurrentSymbol=sYMdownto then begin
*****


C:\Users\Admi\Desktop\btpc-windows>fc btpc2.pas btpc3.pas
Сравнение файлов btpc2.pas и BTPC3.PAS
***** btpc2.pas
    Expect(SymTO);
   end else if CurrentSymbol=TokColon then begin
    Expect(TokColon);
***** BTPC3.PAS
    Expect(SymTO);
    end else if CurrentSymbol=TokColon then begin
    Expect(TokColon);
*****

***** btpc2.pas
begin
 for i:=1 to OutputCodeDataSize do begin
  write(OutputCodeData[i]);
***** BTPC3.PAS
begin
 for i:=1 .. OutputCodeDataSize do begin
  write(OutputCodeData[i]);
*****

***** btpc2.pas
begin
 for i:=1 to 20 do begin
  EmitChar(s[i]);
***** BTPC3.PAS
begin
 for i:=1 .. 20 do begin
  EmitChar(s[i]);
*****

***** btpc2.pas
 { Patch jumps + calls }
 for Index:=1 to CountJumps do begin
  Value:=JumpTable[Index];
***** BTPC3.PAS
 { Patch jumps + calls }
 for Index:=1 .. CountJumps do begin
  Value:=JumpTable[Index];
*****
```

# Тестирование

Тестовый пример:

```pascal
program Hello;


var
  i: Integer;

begin
  for i := 1 .. 10 do
  begin
    WriteLn(i);
  end;
end.
```

Вывод тестового примера на `stdout`

```
1
2
3
4
5
6
7
8
9
10
```

# Вывод
В ходе выполнения лабораторной работы я познакомился с процессом раскрутки самоприменимых компиляторов на 
примере модельного компилятора BeRo. Основной задачей было модифицировать компилятор таким образом, чтобы 
он поддерживал использование знака .. вместо ключевого слова to в циклах for, при этом сохраняя 
возможность использования to.

В процессе работы я изучил исходный код компилятора, внес необходимые изменения в синтаксический 
анализатор и протестировал новую функциональность. В частности, были изменены следующие аспекты:

Изменение в синтаксическом анализаторе: Добавлена поддержка символа .. в качестве альтернативы ключевому 
слову to. Это потребовало модификации проверок ожидаемых символов и обработки нового токена.

Изменение в генерации кода: Внесены изменения в циклы for, чтобы они могли использовать .. вместо to. Это 
было сделано для демонстрации того, что новая функциональность работает корректно.

Тестирование: Написан тестовый пример, который использует новый синтаксис с ... Результат выполнения 
программы подтвердил, что изменения работают корректно, и цикл for с использованием .. выполняется так же, 
как и с использованием to.

В результате выполнения работы я научился:

Анализировать и модифицировать исходный код компилятора.

Работать с синтаксическим анализатором и вносить изменения в грамматику языка.

Тестировать изменения в компиляторе, используя тестовые примеры.

Понимать процесс раскрутки компиляторов и их самоприменимость.

Данная работа позволила мне глубже понять, как устроены компиляторы и как можно модифицировать их для 
поддержки новых возможностей языка.