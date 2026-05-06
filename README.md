![git status](https://compiler-tester.insper-comp.com.br/svg/dudum17/logcomdudu-dp/)
# LogComp – Roteiro 3 (v1.1)

Este repositório contém um interpretador simples de expressões aritméticas inteiras, implementado em Python utilizando um **Lexer** e um **Parser (recursive descent)**.

## Como executar

Requisitos: Python 3

Exemplos de execução no terminal:

```bash
python main.py "3-2"
python main.py "2+3*4"
python main.py "(2+3)*4"
python main.py "-(10-3)"
```

A saída será sempre um número inteiro.

Observação: a divisão é feita utilizando **divisão inteira (`//`)**.

---

## Tokens suportados

O interpretador reconhece os seguintes tokens:

- `INT` — sequência de dígitos
- `+` — operador de soma
- `-` — operador de subtração
- `*` — operador de multiplicação
- `/` — operador de divisão
- `(` — parêntese de abertura
- `)` — parêntese de fechamento
- `EOF` — fim da entrada

---

## EBNF

```ebnf
PROGRAM = { FUNCDEC | STATEMENT } ;
FUNCDEC = "function", IDENTIFIER, "(",(| IDENTIFIER, TYPE, {",", IDENTIFIER, TYPE}),")",(TYPE|), "\n", {STATEMENT}, "end";
BLOCK = "do", {STATEMENT, }, "end" ;
STATEMENT = (|"local", IDENTIFIER, TYPE, ( | "=", BOOLEXPRESSION )|(IDENTIFIER, ("=", BOOLEXPRESSION | "(",(BOOLEXPRESSION, {",", BOOLEXPRESSION} | ),")")) | ("print", "(", BOOLEXPRESSION, ")") | "return", BOOLEXPRESSION |), "\n"| ("if", BOOLEXPRESSION, "then", {STATEMENT}, (|"else", {STATEMENT})), "end" | ("while", BOOLEXPRESSION, "do", {STATEMENT}, "end") | BLOCK;
BOOLEXPRESSION = BOOLTERM, { "or", BOOLTERM } ;
BOOLTERM = RELEXPRESSION, { "and", RELEXPRESSION } ;
RELEXPRESSION = EXPRESSION, {("==" | "<" | ">"), EXPRESSION};
EXPRESSION = TERM, { ("+" | "-"), TERM } ;
TERM = FACTOR, { ("*" | "/"), FACTOR } ;
FACTOR = NUMBER | STRING | BOOLEAN | IDENTIFIER, ("(",(BOOLEXPRESSION, {",", BOOLEXPRESSION} | ),")"|) | ("+" | "-" |"not"), FACTOR | "(", BOOLEXPRESSION, ")" | "read", "(", ")" ;
TYPE = "number" | "string" | "boolean" ;
NUMBER = DIGIT, {DIGIT} ;
IDENTIFIER = LETTER, {LETTER | DIGIT | "_"} ;
STRING = '"..."' ;
DIGIT = "0" | "..." | "9";
LETTER = "a" | "..." | "z" | "A" | "..." | "Z" ;
BOOLEAN = "true" | "false" ;
```
