%{
#include <stdio.h>
#include <stdlib.h>
#define TAG_IDENT 1
#define TAG_NUMBER 2
#define TAG_CHAR 3
#define TAG_KEYWORD 4




char *tag_names[] =
    {
        "END_OF_PROGRAM", "IDENT", "NUMBER",
        "CHAR", "KEYWORD"};
struct Position
{
    int line, pos, index;
};
void print_pos(struct Position *p)
{
    printf("(%d, %d)", p->line, p->pos);
}
struct Fragment
{
    struct Position starting, following;
};
typedef struct Fragment YYLTYPE;
void print_frag(struct Fragment *f)
{
    print_pos(&(f->starting));
    printf("-");
    print_pos(&(f->following));
}
union Token
{
    char* ident;
    int ident_code;
    long num;
    int ch;
};

typedef union Token YYSTYPE;
typedef struct ErrorItem {
    char *key;           // Ключ (строка)
    YYLTYPE value;           // Значение (целое число)
    struct ErrorItem *next; // Указатель на следующий элемент
} ErrorItem;
typedef struct {
    ErrorItem *head; // Указатель на первый элемент
} ErrorList;
ErrorItem *error_item_create(const char *key, YYLTYPE value) {
    ErrorItem *item = (ErrorItem *)malloc(sizeof(ErrorItem));
    item->key = strdup(key); // Копируем ключ
    item->value = value;
    item->next = NULL;
    return item;
}

// Инициализация словаря
void error_init(ErrorList *dict) {
    dict->head = NULL;
}
void error_insert(ErrorList *dict, const char *key, YYLTYPE value) {    
    ErrorItem *item = error_item_create(key, value);
    // Вставляем элемент в начало списка
    item->next = dict->head;
    dict->head = item;
 
}
void error_free(ErrorList *dict) {
    ErrorItem *current = dict->head;
    ErrorItem *next;

    while (current != NULL) {
        next = current->next;
        free(current->key); // Освобождаем память для ключа
        free(current);      // Освобождаем память для элемента
        current = next;
    }
    dict->head = NULL;
}
void error_print(ErrorList *dict) {
    ErrorItem *current = dict->head;
    while (current != NULL) {
        printf("  %s: ", current->key);
        print_frag(&current->value);
        printf("\n");
        current = current->next;
    }
}
typedef struct DictItem {
    char *key;           // Ключ (строка)
    int value;           // Значение (целое число)
    struct DictItem *next; // Указатель на следующий элемент
} DictItem;
typedef struct {
    DictItem *head; // Указатель на первый элемент
} Dict;

// Создание нового элемента словаря
DictItem *dict_item_create(const char *key, int value) {
    DictItem *item = (DictItem *)malloc(sizeof(DictItem));
    item->key = strdup(key); // Копируем ключ
    item->value = value;
    item->next = NULL;
    return item;
}

// Инициализация словаря
void dict_init(Dict *dict) {
    dict->head = NULL;
}
// Поиск элемента по ключу
int dict_find(Dict *dict, const char *key) {
    DictItem *current = dict->head;

    // Проходим по всем элементам списка
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value; // Нашли ключ, возвращаем значение
        }
        current = current->next;
    }

    return -1; // Ключ не найден
}

int dict_insert(Dict *dict, const char *key) {
    int res = dict_find(dict,key);
    if (res == -1) {
        DictItem *prev = dict->head;
        int value_ = 0;
        if (prev != NULL){
            value_ = prev->value + 1 ;
        }
        
        DictItem *item = dict_item_create(key, value_);
        
        // Вставляем элемент в начало списка
        item->next = dict->head;
        
        dict->head = item; 
        return value_;
        }
    return res;
}

// Освобождение памяти, занятой словарем
void dict_free(Dict *dict) {
    DictItem *current = dict->head;
    DictItem *next;

    while (current != NULL) {
        next = current->next;
        free(current->key); // Освобождаем память для ключа
        free(current);      // Освобождаем память для элемента
        current = next;
    }
    dict->head = NULL;
}

// Печать всех элементов словаря
void dict_print(Dict *dict) {
    DictItem *current = dict->head;
    while (current != NULL) {
        printf("  %s: %i", current->key,current->value);
        // print_frag();
        printf("\n");
        current = current->next;
    }
}
static Dict dict;
static ErrorList errors;
int continued;
struct Position cur;
#define YY_USER_ACTION                 \
    {                                  \
        int i;                         \
        if (!continued)                \
            yylloc->starting = cur;    \
        continued = 0;                 \
          for (i = 0; i < yyleng; i++) \
        {                              \
            if (yytext[i] == '\n' )    \
            {                          \
                cur.line++;            \
                cur.pos = 1;           \
            }                          \
            else                       \
                cur.pos++;             \
            cur.index++;               \
        }                              \
          yylloc->following = cur;     \
    }
void init_scanner()
{
    dict_init(&dict);
    error_init(&errors);
    continued = 0;
    cur.line = 1;
    cur.pos = 1;
    cur.index = 0;
}
void err(char *msg,YYLTYPE yylloc)
{
    error_insert(&errors,msg,yylloc);
    /* Бандитизм : ошибки нужно класть в список ошибок . */
    printf(" Error ");
    print_pos(&cur);
    printf(": %s\n", msg);
}

%}

%option noyywrap bison-bridge bison-locations
%x CHAR_1 CHAR_2 
LETTER [a-zA-Z]
DIGIT [0-9]
IDENT {LETTER}({LETTER}|{DIGIT})*{LETTER}
NUMBER {DIGIT}+
HEX [0-9a-fA-F]
KEYWORD z|for|forward
%%
[\n\t\f\v\r ]+
{KEYWORD} { 
    yylval->ident = yytext ;
    return TAG_KEYWORD ;
}
{IDENT} {
    
    yylval->ident_code = dict_insert(&dict,yytext);
    
    return TAG_IDENT ;
    }
    
{NUMBER} {
        yylval -> num = atoi ( yytext );
        return TAG_NUMBER ;
        }

\' {BEGIN (CHAR_1); continued = 1;}
. {
    char s[24] ;
    sprintf(s,"unexpected character %s",yytext);
    err(s, *yylloc);}
<CHAR_1,CHAR_2>\n {
                err (" newline in constant ", *yylloc);
                BEGIN (0);
                yylval -> ch = 0;
                return TAG_CHAR ;
                }
<CHAR_1>\\n {yylval -> ch = '\n' ; BEGIN(CHAR_2); continued = 1;}
<CHAR_1>\\\' {yylval -> ch = '\'' ; BEGIN(CHAR_2); continued = 1;}
<CHAR_1>\\\\ {yylval -> ch = '\\' ; BEGIN(CHAR_2); continued = 1;}
<CHAR_1>\\{HEX}{4} {
    // Обработка шестнадцатеричного символа
    char hex[5];
    strncpy(hex, yytext + 2, 4);
    hex[4] = '\0';
    yylval->ch = (char)strtol(hex, NULL, 16);
    BEGIN(CHAR_2);
    continued = 1;
}
<CHAR_1>\\. {
    err (" unrecognized Escape sequence ", *yylloc);
    yylval -> ch = 0;
    BEGIN (CHAR_2);
    continued = 1;
    }
<CHAR_1>\' {
    err (" empty character literal ", *yylloc);
    BEGIN (0);
    yylval -> ch = 0;
    return TAG_CHAR ;
    }
<CHAR_1>. yylval -> ch = yytext [0]; BEGIN (CHAR_2); continued = 1;
<CHAR_2>\' BEGIN (0); return TAG_CHAR ;
<CHAR_2>[^\n\']* err("too many characters in literal", *yylloc); continued = 1;
%%
# define PROGRAM "Talgat"
int main(int argc, char **argv)
{
    int tag;
    YYSTYPE value;
    YYLTYPE coords;
    FILE *input_file = NULL;

    if (argc > 1)
    {
        // Открываем файл для чтения
        input_file = fopen(argv[1], "r");
        if (!input_file)
        {
            perror("Error opening file");
            return 1;
        }
        // Перенаправляем входной поток на файл
        yyin = input_file;
    }
    else
    {
        // Если файл не указан, читаем из стандартного ввода
        yyin = stdin;
    }

    // Инициализация сканера
    init_scanner ();

    do
    {
        tag = yylex(&value, &coords);
        if (tag != 0)
        {
            printf("Tag: %s", tag_names[tag]);
            print_frag(&coords);
            printf("Value:");
            if (tag == TAG_IDENT )
                printf("%i\n", value.ident_code);
            else if(tag == TAG_KEYWORD)
                printf("%s\n", value.ident);
            else if (tag == TAG_NUMBER)
                printf("%ld\n", value.num);
            else if (tag == TAG_CHAR)
                printf("%c\n", value.ch);
            else
                printf("\n");
        }
    } while (tag != 0);
    printf("Idents");
    dict_print(&dict);
    error_print(&errors);
    // Закрываем файл, если он был открыт
    if (input_file)
        fclose(input_file);
    
    return 0;
}
