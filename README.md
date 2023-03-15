# ll-compiler
Компилятор на питоне, собирающий код из .asm файлов в `.0.bin` и `.1.bin`.
<br/>
Т.к. процессор 64х, а разрядность logisim - 32х, появляется потребность в разделении файла `.o` (то есть результат компиляции) на 2 файла `.bin`.
<br/>
Загрузка кода производится в верхние 2 ОЗУ в схеме main соотвественно (от младшего к старшему, 0 и 1).
<br/>
Загрузка кода в нижние 2 ОЗУ осуществляется, только если есть выполнение команд по Гравардской архитектуре с чтением из ОЗУ. Для этого нужно скомпилировать отдельный код.
# Использование компилятора
Компилятор содержит 3 файла - `database.py`, `compiler.py`, `config.json`.
<br/>
Файл compiler.py парсит код и вызывает его построчное преобразование.
<br/>
Файл database.py хранит информацию о преобразовании.
<br/>
Файл config.json определяет какие файлы и с какими настройками нужно скомпилировать.
<br/>
Чтобы компилятор знал какой файл компилировать, нужно в `config.json` описать `input_files поле`, причем без формата (файл обязательно должен оканчиваться на `.asm`).
<br/>
Результат компиляции будет называться также, файлы типа `.o` и `.0.bin` и `.1.bin`. Располагается в папке описанной в `output_dir`.
<br/>
Также возможно компилировать несколько файлов одновременно.
<br/>
В будущем будет возможность использовать объедиенение файлов и их линковка.
# Синтаксис
Структура записи и чтения - построчно, формат: `flag: command0 args0; command1 args1 #comment`
<br/>
`flag` это ключевое слово (которое создается программистом), обозначающее адрес, на котором flag располагается, ограничивается `:`, не является обязательным параметром, на исполняющий код это не повлияет.
если flag не содержит набор команд после себя - то он **не существует для набора флагов** (то есть данные со значением флага/вызов прыжка по адресу флага, который не имеет команды невозможен), ошибка является вызов такого флага, но никак не его начличие - защита от сложного синтаксиса, позже будут добавлены предупреждения для такого.
<br/>
`command<n>` это операция, `args<n>` это аргументы операции, каждая операция обязяана быть отеделена от другой через точку с запятой, набор опраций на одном адресе сливаются через `XOR`.
<br/>
`#` и все, что после этого ключевого символа, будут считаться коментарием, который не будет участвовать в комиляции.
# Команды
Компилятор (`compiler.py` и `config.json`) это шаблон, который может принять любой `database.py` (вы можете подстроить под свой стиль записи `command<n>` и `args<n>`, создав свой собственный файл).
Текущие команды:
- `dq [flag/uint64_t value]` создает в коде набор данных, значение определяется как uint64_t, если аргумент не число, ведется поиск по флагам, если такой не найдет - ошибка
- `mov [uint64_t address_in_cash_L_1, cash_source source]` записывает в регистер кэша L1 по адресу address_in_cash_L_1 значение от source; source может быть:
  - `RAM` источником выступает ОЗУ (точнее кэш L2, который должен получить эти данные), если соит вместе с `unco` то загрузка прозойдет по адресу из PC, а не из операнда В
  - `ALU` источником выступает АЛУ
  - `PC` источником выступает счетчик программы, указывающий адрес сдвига от начала программы
- `unco` исполнение идет по архитектуре фон Неймана (по умолчаню - Гарвард), за такой запись обазана идти **не команда, а данные** (но можно и без dq, если а в формате генерации кода, если значение должно соотвествовать коду)
- `sel [operand reg, uint64_t index]` выбирает какие регистры подадут значения на АЛУ, index - адрес регистра в cash L1; reg - для какого операнда описание, reg может быть:
  - `A`
  - `B`
- `alu [operation type]` выбирает какую операцию осуществляет АЛУ:
  - `=`   R = A
  - `+`   R = A + B
  - `-`   R = A - B
  - `*`   R = A * B (схема не включена из-за возбуждения)
  - `0`   R = (A * B) % len(A) (схема не включена из-за возбуждения)
  - `/`   R = A / B
  - `%`   R = A % B
  - `!`   R = !A
  - `&`   R = A & B
  - `|`   R = A | B
  - `^`   R = A ^ B
  - `<`   R = A << B
  - `<<`  R = RCL(A, B) 
  - `>`   R = A >> B
  - `>>`  R = RCR(A, B)
  - `b`   R = bool_alu_operation | (count_bits_equals_1(A) << 32)
- `bcv [target_to_controll target]` сообщает, что полученное булевое значение АЛУ имеет управляющую роль; target может быть:
  - `JUMP`  сообщает, что в счетчик адреса команд будет загружено значение из операнда B
  - `PC`    сообщает, что счетчик адреса команд установится в 0
  - `DTC`   сообщает, что операнд B будет исполнен как команда
  - `KILL`  сообщает, что поток убивает себя, устанавливая код на исполнение и счетчик адреса команд в 0
- `bs [bit_source bit]` выбирает какую булевую операцию осуществляет АЛУ, если булевое значение идет в операнд - индекс результата среди битов будет 0; bit может быть:
  - `FALSE`                       выдает false
  - `TRUE`                        выдает true
  - `[bit] [uint64_t bit_index]`  выдает значение бита по индексу bit_index (пример записи: `bs [bit] 32` - выбрать значение 32ого бита), по умолчанию bit_index = 0
  - `>`                           выдает true, если операнд A > операнда B, инчае false             
  - `=`                           выдает true, если операнд A = операнда B, инчае false 
  - `<`                           выдает true, если операнд A < операнда B, инчае false   
  - `+`                           выдает true, если операнд A при сложении с операндом B вызвал переполнение, инчае false 
  - `-`                           выдает true, если операнд B при вычитании из операнда А вызвал переполнение, инчае false 
  - `!`                           выдает true, если операнд A != 0, инчае false
- `write` запись операнда А по адресу из операнда B
- `clr_cash` очиска кэша, любые остальные операции с ним будут недоступны в эту команду
- `goto [address_to_jump flag, register reg]` безусловный прыжок по адресу флага flag, где reg это адрес, куда будет загружен адрес прыжка
# Пример условного перехода
```
#загружаем значение (оно 123)
unco; mov 0 RAM
dq 123
#загружаем значение (оно 321)
unco; mov 1 RAM
dq 321
#загружаем адрес прыжка (он 1000, просто значение от себя, настоятельно советую пользоваться флагами)
unco; mov 2 RAM
dq 1000
#сранвниваем 2 числа (регистр 0 и регистр 1) и сохраняем результат сравнения в бит 0, регистра 3
mov 3 ALU; alu b; bs <; sel A 0; sel B 1
#выполняем прыжок по регистру B если булевое значение ALU это true, а цель контроля - JUMP
#булевое значение получаем по операнду А
bs [bit]; bcv JUMP; sel A 3; sel B 2
```
Итого:
- сама программа заняла - 8 тактов
- условный переход занял - 2 такта
# Пример безусловного перехода
```
#загружаем адрес прыжка (он 1000, просто значение от себя, настоятельно советую пользоваться флагами)
unco; mov 0 RAM
dq 1000
#выполняем прыжок по регистру B если булевое значение ALU это true, а цель контроля - JUMP
#булевое значение получаем как константу (TRUE)
bs TRUE; bcv JUMP
```
Итого:
- сама программа заняла - 3 такта
- безусловный переход занял - 1 такт
# Пример кода на ряде Фибоначе
[Файл](https://github.com/Pasha-2033/ll-compiler/blob/master/input/fibonachi.asm) с комментариями.
# Пример метапрограммирования
Пример метапрограммирования на asm это использование занчения регистров как аргументов команд.
Без команды `bcv DTC` не обойтись. Ведь мы хотим использовтать данные как код, например если мы хотим положить по созданному индексу значение из RAM.
Что-то типа mov (sel B 0) RAM. Запись в регистр по индексу из операнда B по источнику RAM.
```
#загружаем команду как данные (ибо unco считает, что после нее идут данные)
unco; mov 0 RAM
unco; mov 2 RAM;
#загружаем индекс для регистра (он 5, но из-за сдвига влево на 22, оно больше)
#если нет гарантий, что индекс будет иметь биты = 1 кроме бит 22-35, то следует сделать index & 0xfffc00000 (или что-то в этом духе), а потом его использовать
mov 1 RAM
dq 20971520
#получаем итогововую команду на исполнение (помним, что она в кэше L1, а не в кэше L2, где она моет быть прочитана как команда по PC!)
mov 0 ALU; alu |; sel A 0; sel B 1
#нам совершенно не важно где произойдет чтение, важно куда, но для простоты загрузим значение не по адресу операнда B, а по PC
#также очень важно учитывать, то unco в метакоманде продолжит рост PC, а дальнейший код после метакоманд будет начинаться с кол-вом сдвигов равномному кол-ву unco в метакомандах
bcv DTC; sel B 0
dq 123
#в итоге у нас загрузилось 123 в регистр 5, насмотря на то, что у нас нет команды "mov 5 <cash_source>"
```
Итого:
- сама программа заняла - 7 тактов
- метакоманда заняла - 1 такт
- создание метакоманды занало - 4
