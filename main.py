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

    def set_value(self, name, value_var):
        if name not in self.table:
            raise Exception("[Semantic] error code")
        if not isinstance(value_var, Variable):
            raise Exception("[Semantic] error code")
        var = self.table[name]
        if var.type != value_var.type:
            raise Exception("[Semantic] error code")
        var.value = value_var.value
    
    def create_variable(self, name, vtype, value):
        if name in self.table:
            raise Exception("[Semantic] error code")
        self.table[name] = Variable(vtype, value)
    
    def get_value(self, var):
        if var in self.table:
            return self.table[var]
        else:
            raise Exception("[Semantic] error code")


class Variable:
     def __init__(self, type, value):
        self.type = type
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
        return Variable("number", self.value)

class BoolVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return Variable("boolean", self.value)
    
class StringVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return Variable("string", self.value)


class UnOp(Node):
    def __init__(self, value: str, children: list["Node"]):
          super().__init__(value, [children])

    def evaluate(self, st):
        val = self.children[0].evaluate(st)
        if self.value == "+":
            return val
        elif self.value == "-":
            return -(val)
        elif self.value == "not":
            return not(val)


class BinOp(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        left = self.children[0].evaluate(st)
        right = self.children[1].evaluate(st)

        if not isinstance(left, Variable) or not isinstance(right, Variable):
            raise Exception("[Semantic] error code")

        if self.value == "+":
            if left.type == "number" and right.type == "number":
                return Variable("number", left.value + right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "-":
            if left.type == "number" and right.type == "number":
                return Variable("number", left.value - right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "*":
            if left.type == "number" and right.type == "number":
                return Variable("number", left.value * right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "/":
            if left.type == "number" and right.type == "number":
                if right.value == 0:
                    raise Exception("[Semantic] error code")
                return Variable("number", left.value // right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "and":
            if left.type == "boolean" and right.type == "boolean":
                return Variable("boolean", left.value and right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "or":
            if left.type == "boolean" and right.type == "boolean":
                return Variable("boolean", left.value or right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "==":
            if left.type == right.type:
                return Variable("boolean", left.value == right.value)
            raise Exception("[Semantic] error code")

        elif self.value == "<":
            if left.type == "number" and right.type == "number":
                return Variable("boolean", left.value < right.value)
            raise Exception("[Semantic] error code")

        elif self.value == ">":
            if left.type == "number" and right.type == "number":
                return Variable("boolean", left.value > right.value)
            raise Exception("[Semantic] error code")

        raise Exception("[Semantic] error code")

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
        print(val.value)
        return val

class Assignment(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        varname = self.children[0].value
        varvalue = self.children[1].evaluate(st)
        st.set_value(varname, varvalue)
        return varvalue
    

class If (Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
       condicao = self.children[0].evaluate(st)
       if condicao.type != "boolean":
            raise Exception("[Semantic] error code")
       if condicao.value:
            return self.children[1].evaluate(st)
       elif len(self.children) > 2:
            return self.children[2].evaluate(st)
       return None
class While (Node):
    def __init__(self, value: str, children: list["Node"]):
         super().__init__(value, children)
    
    def evaluate(self, st):
        res = None
        condicao = self.children[0].evaluate(st)

        if condicao.type != "boolean":
            raise Exception("[Semantic] error code")

        while condicao.value:
            res = self.children[1].evaluate(st)
            condicao = self.children[0].evaluate(st)

            if condicao.type != "boolean":
                raise Exception("[Semantic] error code")

        return res
class VarDec(Node):
    def __init__(self, value, children):
        super().__init__(value, children)
    def evaluate(self, st):
        name = self.children[0].value
        if len(self.children) == 1:
            st.create_variable(name, self.value, None)
            return None
        else:
            init_val: Variable  = self.children[1].evaluate(st)
            if init_val.type != self.value:
                raise Exception("[Semantic] error code")
            st.create_variable(name, self.value, init_val.value)
            return init_val
    
class Read(Node):
     def __init__(self, value, children):
        super().__init__(value, children)

     def evaluate(self, st):
        try:
            return int(input())
        except ValueError:
            raise Exception("[Semantic] error code")

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
       elif caracter == '>':
            self.next = Token("GT", '>')
            self.position += 1
       elif caracter == '<':
            self.next = Token("LT", '<')
            self.position += 1
       elif caracter == "=":
            if self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "==":
                self.next = Token("EQ", "==")
                self.position += 2
            else:
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
       elif caracter == '"' or caracter == "'":
             quote = caracter  # guarda o tipo de aspa usada
             self.position += 1
             str_val = ""
             while self.position < len(self.source) and self.source[self.position] != quote:
                   str_val += self.source[self.position]
                   self.position += 1
             if self.position >= len(self.source):
                   raise Exception("String não terminada")
             self.position += 1  # consome a aspa final
             self.next = Token("STR", str_val)   
       elif caracter.isalpha() or caracter == "_":
            ident = ""
            while (self.position < len(self.source)
                   and (self.source[self.position].isalnum() or self.source[self.position] == "_")):
                ident += self.source[self.position]
                self.position += 1
            if ident == "print":
                self.next = Token("PRINT", ident)
            elif ident == "and":
                self.next = Token("AND", ident)
            elif ident == "or":
                self.next = Token("OR", ident)
            elif ident == "not":
                self.next = Token("NOT", ident)
            elif ident == "if":
                self.next = Token("IF", ident)
            elif ident == "while":
                self.next = Token("WHILE", ident)
            elif ident == "else":
                self.next = Token("ELSE", ident)
            elif ident == "read":
                self.next = Token("READ", ident)
            elif ident == "then":
                self.next = Token("OPEN_IF_BRA", ident)
            elif ident == "do":
                self.next = Token("OPEN_BRA", ident)
            elif ident == "end":
                self.next = Token("CLOSE_BRA", ident)
            elif ident == "local":
                self.next = Token("VAR", ident)
            elif ident in ("true", "false"):
                self.next = Token("BOOL", ident)
            elif ident in ("string", "number", "boolean"):
                self.next = Token("TYPE", ident)
            else:
                self.next = Token("IDEN", ident)
       else:
            raise Exception("[Lexer] error code")

class Parser:
    lexer = None
    symbol_table = None

    @staticmethod
    def parse_rel_expression():
        left = Parser.parse_expression()
        if Parser.lexer.next.kind in ("EQ", "LT", "GT"):
             op = Parser.lexer.next.kind
             Parser.lexer.select_next()
             rigth = Parser.parse_expression()
             if op == "EQ":
                 return BinOp("==", [left, rigth])
             elif op == "LT":
                  return BinOp("<", [left, rigth])
             elif op == "GT":
                  return BinOp(">", [left, rigth])
        return left
                 

    
    @staticmethod
    def parse_bool_term():
        res = Parser.parse_rel_expression()
        while Parser.lexer.next.kind == "AND":
            Parser.lexer.select_next()
            res = BinOp("and", [res, Parser.parse_rel_expression()])
        return res

    @staticmethod
    def parse_bool_expression():
        res = Parser.parse_bool_term()
        while Parser.lexer.next.kind == "OR":
            Parser.lexer.select_next()
            res = BinOp("or", [res, Parser.parse_bool_term()])
        return res


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
        elif Parser.lexer.next.kind == "NOT":
            Parser.lexer.select_next()
            res = UnOp("not", Parser.parse_factor())
            return res
        elif Parser.lexer.next.kind == "OPEN_PAR":
            Parser.lexer.select_next()
            res = Parser.parse_bool_expression()
            if Parser.lexer.next.kind != "CLOSE_PAR":
                raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            return res
        elif Parser.lexer.next.kind == "READ":
            Parser.lexer.select_next()
            if Parser.lexer.next.kind != "OPEN_PAR":
               raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            if Parser.lexer.next.kind != "CLOSE_PAR":
              raise Exception("[Parser] error code")
            Parser.lexer.select_next()
            return Read("read", [])
        elif Parser.lexer.next.kind == "STR":
           
           res = StringVal(Parser.lexer.next.value, [])
           Parser.lexer.select_next()
           return res
        elif Parser.lexer.next.kind == "BOOL":
           val = True if Parser.lexer.next.value == "true" else False
           res = BoolVal(val, [])
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

        if Parser.lexer.next.kind == "VAR":
          Parser.lexer.select_next()  # consome 'local'

          if Parser.lexer.next.kind != "IDEN":
              raise Exception("[Parser] error code")
          ident = Identifier(Parser.lexer.next.value, [])
          Parser.lexer.select_next()

          if Parser.lexer.next.kind != "TYPE":
              raise Exception("[Parser] error code")
          vtype = Parser.lexer.next.value
          Parser.lexer.select_next()

          if Parser.lexer.next.kind == "ASSIGN":
            Parser.lexer.select_next()
            expr = Parser.parse_bool_expression()

            if Parser.lexer.next.kind == "END":
                Parser.lexer.select_next()
                return VarDec(vtype, [ident, expr])
            elif Parser.lexer.next.kind == "EOF":
                return VarDec(vtype, [ident, expr])
            else:
                raise Exception("[Parser] error code")
          else:
             if Parser.lexer.next.kind == "END":
                Parser.lexer.select_next()
                return VarDec(vtype, [ident])
             elif Parser.lexer.next.kind == "EOF":
                return VarDec(vtype, [ident])
             else:
                raise Exception("[Parser] error code")

        if Parser.lexer.next.kind == "IDEN":
            ident = Identifier(Parser.lexer.next.value, [])
            Parser.lexer.select_next()
            if Parser.lexer.next.kind == "ASSIGN":
                Parser.lexer.select_next()
                expr = Parser.parse_bool_expression()
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
            expr = Parser.parse_bool_expression()
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
        elif Parser.lexer.next.kind == "WHILE":
             Parser.lexer.select_next()
             cond = Parser.parse_bool_expression()

             if Parser.lexer.next.kind != "OPEN_BRA":   # do
               raise Exception("[Parser] error code")
             Parser.lexer.select_next()

             children = []
             while Parser.lexer.next.kind != "CLOSE_BRA":   # end
               stmt = Parser.parse_statement()
               if stmt is not None:
                  children.append(stmt)

             Parser.lexer.select_next()   # consome o end
             return While("while", [cond, Block("block", children)])
        elif  Parser.lexer.next.kind == "IF":
            Parser.lexer.select_next()
            cond = Parser.parse_bool_expression()

            if Parser.lexer.next.kind != "OPEN_IF_BRA":   # then
              raise Exception("[Parser] error code")
            Parser.lexer.select_next()

            then_children = []
            while Parser.lexer.next.kind not in ("ELSE", "CLOSE_BRA"):
              stmt = Parser.parse_statement()
              if stmt is not None:
                 then_children.append(stmt)

            children = [cond, Block("block", then_children)]

            if Parser.lexer.next.kind == "ELSE":
                Parser.lexer.select_next()

                else_children = []
                while Parser.lexer.next.kind != "CLOSE_BRA":
                  stmt = Parser.parse_statement()
                  if stmt is not None:
                    else_children.append(stmt)

                children.append(Block("block", else_children))

            if Parser.lexer.next.kind != "CLOSE_BRA":
                raise Exception("[Parser] error code")

            Parser.lexer.select_next()   # consome o end
            return If("if", children)
        
        elif Parser.lexer.next.kind == "OPEN_BRA":
            return Parser.parse_block()
        elif Parser.lexer.next.kind == "END":
            Parser.lexer.select_next()
            return NoOp(None, [])
        else:
             expr = Parser.parse_bool_expression()
             if Parser.lexer.next.kind == "END":
                  Parser.lexer.select_next()
                  return expr
             elif Parser.lexer.next.kind == "EOF":
                 return expr
             else:
                 raise Exception("[Parser] error code")
   

    

    @staticmethod
    def parse_block():
        if Parser.lexer.next.kind != "OPEN_BRA":
            raise Exception("[Parser] error code")
        Parser.lexer.select_next()
        children = []
        while Parser.lexer.next.kind not in ("CLOSE_BRA", "EOF"):
            stmt = Parser.parse_statement()
            if stmt is not None:
                children.append(stmt)
        if Parser.lexer.next.kind != "CLOSE_BRA":
            raise Exception("[Parser] error code")
        Parser.lexer.select_next()
        return Block("block", children)
    
   
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
        return res.evaluate(Parser.symbol_table)

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
    Parser.symbol_table = SymbolTable()
    Parser.run(novo_codigo)
    


if __name__ == "__main__":
    main()