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
Expression  = Term , { ("+" | "-") , Term } ;
Term        = Factor , { ("*" | "/") , Factor } ;
Factor      = [ ("+" | "-") ] , ( INT | "(" , Expression , ")" ) ;
INT         = Digit , { Digit } ;
Digit       = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```