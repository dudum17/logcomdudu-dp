import sys
import re
from abc import ABC, abstractmethod
from typing import Any

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class Node(ABC):
    def __init__(self, value : str, children : list["Node"]):
        self.value = value
        self.children = children
    
    @abstractmethod
    def evaluate(self):
        pass

class IntVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self):
        return self.value
    

class UnOp(Node):
    def __init__(self, value: str, children: list["Node"]):
          super().__init__(value, [children])

    def evaluate(self):
        val = self.children[0].evaluate()
        if self.value == "+":
            return val
        elif self.value == "-":
            return -(val)
        

class BinOp(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self):
        left = self.children[0].evaluate()
        right = self.children[1].evaluate()

        if self.value == "+":
            return left + right
        elif self.value == "-":
            return left - right
        elif self.value == "*":
            return left * right
        elif self.value == "/":
            if right == 0:
                raise Exception("[Semantic] error code")
            return left // right
class Lexer:
    def __init__(self, source, position):
        self.source = source
        self.position = position
        self.next = None

    def select_next(self):
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1

        if self.position >= len(self.source):
            self.next = Token("EOF", "")
            return

        caracter = self.source[self.position]

        if caracter == '+':
            self.next = Token("PLUS", '+')
            self.position += 1
        elif caracter == '-':
            self.next = Token("MINUS", '-')
            self.position += 1
        elif caracter == '*':
            self.next = Token("MULT", '*')
            self.position += 1
        elif caracter == '/':
            self.next = Token("DIV", '/')
            self.position += 1
        elif caracter == '(':
            self.next = Token("OPEN_PAR", '(')
            self.position += 1
        elif caracter == ')':
            self.next = Token("CLOSE_PAR", ')')
            self.position += 1
        elif caracter.isdigit():
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("INT", num)
        else:
            raise Exception("[Lexer] error code")

class Parser:
    lexer = None

    @staticmethod
    def parse_factor():
        if Parser.lexer.next.kind == "INT":
            res = IntVal(int(Parser.lexer.next.value), [])
            Parser.lexer.select_next()
            return res

        elif Parser.lexer.next.kind == "PLUS":
            Parser.lexer.select_next()
            res = UnOp("+", Parser.parse_factor())
            return res
        elif Parser.lexer.next.kind == "MINUS":
             Parser.lexer.select_next()
             res = UnOp("-", Parser.parse_factor())
             return res
        elif Parser.lexer.next.kind == "OPEN_PAR":
            Parser.lexer.select_next()
            res = Parser.parse_expression()
            if Parser.lexer.next.kind != "CLOSE_PAR":
                raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            return res
        else:
            raise Exception("[Parser] error code")

    @staticmethod
    def parse_term():
            res = Parser.parse_factor()

            while Parser.lexer.next.kind in ("MULT", "DIV"):
               op = Parser.lexer.next.kind
               Parser.lexer.select_next()

               if op == "MULT":
                   res = BinOp("*", [res, Parser.parse_factor()])
               elif op == "DIV":
                  res = BinOp("/", [res, Parser.parse_factor()])

            return res

    @staticmethod
    def parse_expression():
             res = Parser.parse_term()

             while Parser.lexer.next.kind in ("PLUS", "MINUS"):
               op = Parser.lexer.next.kind
               Parser.lexer.select_next()

               if op == "PLUS":
                   res = BinOp("+", [res, Parser.parse_term()])
               elif op == "MINUS":
                    res = BinOp("-", [res, Parser.parse_term()])

             return res
    @staticmethod
    def run(code):
        Parser.lexer = Lexer(code, 0)
        Parser.lexer.select_next()
        res = Parser.parse_expression()

        if Parser.lexer.next.kind != "EOF":
            raise Exception("[Parser] error code")
        return res.evaluate()

def main():
    if len(sys.argv) != 2:
        print('Uso: python main.py "expressão"')
        sys.exit(1)

    print(Parser.run(sys.argv[1]))

if __name__ == "__main__":
    main()