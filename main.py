import sys
import re
from abc import ABC, abstractmethod
from typing import Any

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class PrePro:
    @staticmethod
    def filter(code):
        return re.sub(r"--[^\n]*", "", code)
    
class SymbolTable:
    def __init__(self):
        self.table = {}
    
    def set_value(self, var, value):
        self.table[var] = value 

    def get_value(self, var):
        if var in self.table:
            return self.table[var]
        else:
            raise Exception("[Semantic] error code")


class Variable:
    def __init__(self, value):
        self.value = value

class Node(ABC):
    def __init__(self, value : str, children : list["Node"]):
        self.value = value
        self.children = children
    
    @abstractmethod
    def evaluate(self, st : SymbolTable):
        pass

class IntVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return self.value
    

class UnOp(Node):
    def __init__(self, value: str, children: list["Node"]):
          super().__init__(value, [children])

    def evaluate(self, st):
        val = self.children[0].evaluate(st)
        if self.value == "+":
            return val
        elif self.value == "-":
            return -(val)
        

class BinOp(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        left = self.children[0].evaluate(st)
        right = self.children[1].evaluate(st)

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

class Identifier(Node):
     def __init__(self, value, children):
         super().__init__(value, children)
     def evaluate(self, st):
         return st.get_value(self.value)
     
class Print(Node):
    def __init__(self, value, children):
        super().__init__(value, [children])
    def evaluate(self, st):
        val = self.children[0].evaluate(st)
        print(val)
        return val
    
class Assignment(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        varname = self.children[0].value
        varvalue = self.children[1].evaluate(st)
        st.set_value(varname, varvalue)
        return varvalue

class Block(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        for child in self.children:
            child.evaluate(st)


class NoOp(Node):
    def __init__(self, value, children):
        super().__init__(value, children)
    
    def evaluate(self, st):
        return None



class Lexer:
    def __init__(self, source, position):
        self.source = source
        self.position = position
        self.next = None

    def select_next(self):
       while self.position < len(self.source) and self.source[self.position] in " \t":
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
       elif caracter == "=":
            self.next = Token("ASSIGN", "=")
            self.position += 1
       elif caracter == "\n":
            self.next = Token("END", " ")
            self.position += 1
       elif caracter.isdigit():
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("INT", num)
       elif caracter.isalpha() or caracter == "_":
            ident = ""
            while (self.position < len(self.source)
                   and (self.source[self.position].isalnum() or self.source[self.position] == "_")):
                ident += self.source[self.position]
                self.position += 1
            if ident == "print":
                self.next = Token("PRINT", ident)
            else:
                self.next = Token("IDEN", ident)
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
        elif Parser.lexer.next.kind == "IDEN":
            res = Identifier(Parser.lexer.next.value, [])
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
    def parse_statement():
        if Parser.lexer.next.kind == "IDEN":
            ident = Identifier(Parser.lexer.next.value, [])
            Parser.lexer.select_next()
            if Parser.lexer.next.kind == "ASSIGN":
                Parser.lexer.select_next()
                expr = Parser.parse_expression()
                if Parser.lexer.next.kind == "END":
                    Parser.lexer.select_next()
                    return Assignment("=", [ident, expr])
                elif Parser.lexer.next.kind == "EOF":
                    return Assignment("=", [ident, expr])
                else:
                    raise Exception("[Parser] error code")
            else:
                raise Exception("[Parser] error code")
        
        elif Parser.lexer.next.kind == "PRINT":
            Parser.lexer.select_next()
            if Parser.lexer.next.kind != "OPEN_PAR":
                raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            expr = Parser.parse_expression()
            if Parser.lexer.next.kind != "CLOSE_PAR":
                raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            if Parser.lexer.next.kind == "END":
                Parser.lexer.select_next()
                return Print("print", expr)
            elif Parser.lexer.next.kind == "EOF":
                return Print("print", expr)
            else:
                raise Exception("[Parser] error code")
        elif Parser.lexer.next.kind == "END":
            Parser.lexer.select_next()
            return NoOp(None, [])
        else:
             expr = Parser.parse_expression()
             if Parser.lexer.next.kind == "END":
                  Parser.lexer.select_next()
                  return expr
             elif Parser.lexer.next.kind == "EOF":
                 return expr
             else:
                 raise Exception("[Parser] error code")

    @staticmethod
    def parse_program():
         children = []
         while Parser.lexer.next.kind != "EOF":
             stmt = Parser.parse_statement()
             children.append(stmt)
         return Block("block", children)
             
    @staticmethod
    def run(code):
        Parser.lexer = Lexer(code, 0)
        Parser.lexer.select_next()
        res = Parser.parse_program()
        if Parser.lexer.next.kind != "EOF":
            raise Exception("[Parser] error code")
        st = SymbolTable()
        return res.evaluate(st)

def main():
    if len(sys.argv) != 2:
        print('Uso: python main.py "expressão"')
        sys.exit(1)

    arquivo = sys.argv[1]
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo}' não encontrado.")
        sys.exit(1)

    novo_codigo = PrePro.filter(codigo)
    Parser.run(novo_codigo)
    


if __name__ == "__main__":
    main()