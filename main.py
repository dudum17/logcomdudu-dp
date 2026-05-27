import sys
import re
from abc import ABC, abstractmethod
from typing import Any
import os

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class PrePro:
    @staticmethod
    def filter(code):
        code = re.sub(r"--[^\n]*", "", code)

        constants = {}
        lines = code.split("\n")
        new_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("const "):
                match = re.match(r"const\s+([A-Za-z_]\w*)\s*(?:=\s*)?(.+)", stripped)

                if not match:
                    raise Exception("[Parser] error code")

                name = match.group(1)
                value = match.group(2).strip()

                constants[name] = value
            else:
                new_lines.append(line)

        code = "\n".join(new_lines)

        for name, value in constants.items():
            code = re.sub(rf"\b{name}\b", value, code)

        return code

class SymbolTable:
    def __init__(self, parent = None):
        self.table = {}
        self.counter = 0 
        self.parent = parent

    def set_value(self, name, value_var):
        if name in self.table:
            if not isinstance(value_var, Variable):
                raise Exception("[Semantic] error code")

            var = self.table[name]

            if var.type != value_var.type:
                raise Exception("[Semantic] error code")

            if var.immutable:
               raise Exception("[Semantic] error code")
            var.value = value_var.value
            return

        if self.parent is not None:
         self.parent.set_value(name, value_var)
         return

        self.create_variable(name, value_var.type, value_var.value)
        return
    
    def create_variable(self, name, vtype, value,
                    is_function = False,
                    immutable = False):
        if name in self.table:
            raise Exception("[Semantic] error code")
        self.counter += 4
        self.table[name] = Variable(vtype, value, -self.counter, is_function, immutable)
    
    def get_value(self, var):
        if var in self.table:
            return self.table[var]

        if self.parent is not None:
            return self.parent.get_value(var)

        raise Exception("[Semantic] error code")


class Variable:
     def __init__(self, type, value, shift = None,
                  is_function = False,
                  immutable = False):

        self.type = type
        self.value = value
        self.shift = shift
        self.is_function = is_function
        self.immutable = immutable

class Code:
    instructions = []

    @staticmethod
    def append(code):
        Code.instructions.append(code)

    @staticmethod
    def dump(filename: str) -> None:
         with open(filename, 'w') as file:
             file.write("section .data\n")
             file.write("  format_out: db \"%d\", 10, 0 ; format do printf\n")
             file.write("  format_in: db \"%d\", 0 ; format do scanf\n")
             file.write("  scan_int: dd 0; 32-bits integer\n\n")
             file.write("section .text\n\n")
             file.write("  extern printf ; usar _printf para Windows\n")
             file.write("  extern scanf ; usar _scanf para Windows\n")
             file.write("  ; extern _ExitProcess@4 ; usar para Windows\n")
             file.write("  global _start ; início do programa\n\n")
             file.write("_start:\n")
             file.write("  push ebp ; guarda o EBP\n")
             file.write("  mov ebp, esp ; zera a pilha\n\n")
             file.write("  ; aqui começa o codigo gerado:\n\n")
             file.write("\n".join(Code.instructions))
             file.write("\n\n  ; aqui termina o código gerado\n\n")
             file.write("  mov esp, ebp ; reestabelece a pilha\n")
             file.write("  pop ebp\n\n")
             file.write("  ; chamada da interrupcao de saida (Linux)\n")
             file.write("  mov eax, 1   \n")
             file.write("  xor ebx, ebx \n")
             file.write("  int 0x80     \n")
             file.write("  ; Para Windows:\n")
             file.write("  ; push dword 0        \n")
             file.write("  ; call _ExitProcess@4\n")

        

class Node(ABC):
    id = 0

    def __init__(self, value : str, children : list["Node"]):
        self.value = value
        self.children = children
        self.id = Node.new_id()

    @abstractmethod
    def evaluate(self, st : SymbolTable):
        pass

    @abstractmethod
    def generate(self, st : SymbolTable):
        pass

    @staticmethod
    def new_id():
        Node.id += 1
        return Node.id

class IntVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return Variable("number", self.value)
    
    def generate(self, st):
        Code.append(f"  mov eax, {self.value}")


class BoolVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return Variable("boolean", self.value)
    
    def generate(self, st):
        Code.append(f"  mov eax, {1 if self.value else 0}")
    
class StringVal(Node):
    def __init__(self, value : str,  children ):
        super().__init__(value, children)

    def evaluate(self, st):
        return Variable("string", self.value)
    
    def generate(self, st):
        pass



class UnOp(Node):
    def __init__(self, value: str, children: list["Node"]):
          super().__init__(value, [children])

    def evaluate(self, st):
        val = self.children[0].evaluate(st)

        if not isinstance(val, Variable):
            raise Exception("[Semantic] error code")

        if self.value == "+":
            if val.type == "number":
                return Variable("number", val.value)
            raise Exception("[Semantic] error code")

        elif self.value == "-":
            if val.type == "number":
                return Variable("number", -val.value)
            raise Exception("[Semantic] error code")

        elif self.value == "not":
            if val.type == "boolean":
                return Variable("boolean", not val.value)
            raise Exception("[Semantic] error code")

        raise Exception("[Semantic] error code")
    def generate(self, st):
        self.children[0].generate(st)
        if self.value == "-":
            Code.append(f"neg eax")
        elif self.value == "not":
            Code.append("  cmp eax, 0")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmove eax, ecx")

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
        

        elif self.value == "..":
           def to_string(var):
             if var.type == "boolean":
                return "true" if var.value else "false"
             return str(var.value)

           return Variable("string", to_string(left) + to_string(right))

        elif self.value == "<":
          if left.type == "number" and right.type == "number":
            return Variable("boolean", left.value < right.value)
          if left.type == "string" and right.type == "string":
            return Variable("boolean", left.value < right.value)
          raise Exception("[Semantic] error code")


        elif self.value == ">":
            if left.type == "number" and right.type == "number":
              return Variable("boolean", left.value > right.value)
            if left.type == "string" and right.type == "string":
                return Variable("boolean", left.value > right.value)
            raise Exception("[Semantic] error code")

        raise Exception("[Semantic] error code")
    def generate(self, st):
        self.children[1].generate(st)
        Code.append("  push eax")
        self.children[0].generate(st)
        Code.append("  pop ecx")
        if self.value == "+":
             Code.append("  add eax, ecx")
        elif self.value == "-":
             Code.append("  sub eax, ecx")
        elif self.value == "*":
             Code.append("  imul ecx")
        elif self.value == "/":
            Code.append("  cdq")
            Code.append("  idiv ecx")
        elif self.value == "and":
            Code.append("  and eax, ecx")
        elif self.value == "or":
            Code.append("  or eax, ecx")
        elif self.value == "==":
          Code.append("  cmp eax, ecx")
          Code.append("  mov eax, 0")
          Code.append("  mov ecx, 1")
          Code.append("  cmove eax, ecx")
        elif self.value == ">":
          Code.append("  cmp eax, ecx")
          Code.append("  mov eax, 0")
          Code.append("  mov ecx, 1")
          Code.append("  cmovg eax, ecx")
        elif self.value == "<":
          Code.append("  cmp eax, ecx")
        # ordem do gabarito:
          Code.append("  mov eax, 0")
          Code.append("  mov ecx, 1")
          Code.append("  cmovl eax, ecx")
        else:
             raise Exception(f"Generate não implementado para operador '{self.value}'")

class Identifier(Node):
     def __init__(self, value, children):
         super().__init__(value, children)
     def evaluate(self, st):
         return st.get_value(self.value)
     def generate(self, st):
         var = st.get_value(self.value)
         Code.append(f"  mov eax, [ebp{var.shift}]")

class Print(Node):
    def __init__(self, value, children):
        super().__init__(value, [children])
    def evaluate(self, st):
       val = self.children[0].evaluate(st)

       if val.type == "boolean":
            print("true" if val.value else "false")
       else:
            print(val.value)

       return val

    def generate(self, st):
        self.children[0].generate(st)
        Code.append("  push eax ; empilha f")
        Code.append("  push format_out ; formato int de saida")
        Code.append("  call printf ; Print f")
        Code.append("  add esp, 8 ; limpa os argumentos")

class Assignment(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        varname = self.children[0].value
        varvalue = self.children[1].evaluate(st)
        st.set_value(varname, varvalue)
        return varvalue
    def generate(self, st):
        ident_node = self.children[0]
        expr_node = self.children[1]
        expr_node.generate(st)
        var = st.get_value(ident_node.value)
        Code.append(f"  mov [ebp{var.shift}], eax ; {ident_node.value} = { 'Scan()' if isinstance(expr_node, Read) else ''}")
    

class If (Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
       condicao = self.children[0].evaluate(st)
       if condicao.type != "boolean":
            raise Exception("[Semantic] error code")
       if condicao.value:
            res = self.children[1].evaluate(st)
            if isinstance(res, tuple) and res[0] == "return":
                return res
       elif len(self.children) > 2:
             res = self.children[2].evaluate(st)
             if isinstance(res, tuple) and res[0] == "return":
                  return res
       return None
    def generate(self, st):
        label_else = f"else_{self.id}"
        label_end  = f"endif_{self.id}"

        self.children[0].generate(st)
        Code.append("  cmp eax, 0")

        if len(self.children) > 2:
             # if ... else ...
            Code.append(f"  je {label_else}")
            self.children[1].generate(st)       # bloco do if
            Code.append(f"  jmp {label_end}")   # pula o else
            Code.append(f"{label_else}:")
            self.children[2].generate(st)       # bloco do else
            Code.append(f"{label_end}:")
        else:
             # if simples
            Code.append(f"  je {label_end}")
            self.children[1].generate(st)
        Code.append(f"{label_end}:")


class IfExpr(Node):
    def __init__(self, value, children):
        super().__init__(value, children)

    def evaluate(self, st):
        cond = self.children[0].evaluate(st)

        if cond.type != "boolean":
            raise Exception("[Semantic] error code")

        if cond.value:
            return self.children[1].evaluate(st)
        else:
            return self.children[2].evaluate(st)

    def generate(self, st):
        pass

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
            if isinstance(res, tuple) and res[0] == "return":
                  return res
            condicao = self.children[0].evaluate(st)

            if condicao.type != "boolean":
                raise Exception("[Semantic] error code")

        return res
    def generate(self, st):
        label_loop =  f"loop_{self.id}"
        label_exit =  f"exit_{self.id}"

        Code.append(f"  {label_loop}: ; label do loop ")
        self.children[0].generate(st)
        Code.append("  cmp eax, 0 ; se a condição for falsa, sai")
        Code.append(f"  je {label_exit}")
        self.children[1].generate(st)
        Code.append(f"  jmp {label_loop}")
        Code.append(f"  {label_exit}:")


class VarDec(Node):
    def __init__(self, value, children, immutable=False):
        super().__init__(value, children)
        self.immutable = immutable
    def evaluate(self, st):
        name = self.children[0].value
        if len(self.children) == 1:
            st.create_variable(
              name,
              self.value,
              None,
              immutable=self.immutable)
            return None
        else:
            init_val: Variable  = self.children[1].evaluate(st)
            vtype = self.value

            if vtype is None:
              vtype = init_val.type

            if init_val.type != vtype:
                raise Exception("[Semantic] error code")
            st.create_variable(
             name,
             vtype,
             init_val.value,
             immutable=self.immutable)
            return init_val
    def generate(self, st):
        name = self.children[0].value
        var = st.get_value(name)

        Code.append(f"  sub esp, 4 ; var {name} int [EBP{var.shift}]")

        if len(self.children) > 1:
            self.children[1].generate(st)
            Code.append(f"  mov [ebp{var.shift}], eax ; {name} = "
                        f"{self.children[1].value if isinstance(self.children[1], IntVal) else ''}")


class FuncDec(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        func_name = self.children[0].value

        st.create_variable(func_name, "function", self, True)

        return None
    def generate(self, st):
        pass
class FuncCall(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        func_var = st.get_value(self.value)

        if func_var.type != "function":
            raise Exception("[Semantic] error code")

        func_node = func_var.value

        return_type = func_node.value
        params = func_node.children[1:-1]
        body = func_node.children[-1]

        if len(self.children) != len(params):
            raise Exception("[Semantic] error code")

        func_st = SymbolTable(st)

        for param_node, arg_node in zip(params, self.children):
            param_name = param_node.children[0].value
            param_type = param_node.value

            arg_value = arg_node.evaluate(st)

            if arg_value.type != param_type:
                raise Exception("[Semantic] error code")

            func_st.create_variable(param_name, param_type, arg_value.value)

        result = body.evaluate(func_st)

        if result is None:
           if return_type == "void":
               return Variable("void", None)
           raise Exception("[Semantic] error code")
        if not (isinstance(result, tuple) and result[0] == "return"):
            raise Exception("[Semantic] error code")

        return_value = result[1]


        if return_type == "void":
           raise Exception("[Semantic] error code")


        if return_value.type != return_type:
            raise Exception("[Semantic] error code")

        return return_value
    def generate(self, st):
        pass

class Return(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
        val = self.children[0].evaluate(st)
        return ("return", val)
    def generate(self, st):
        pass

class For(Node):
    def __init__(self, value, children):
        super().__init__(value, children)

    def evaluate(self, st):
        var_name = self.children[0].value
        start_val = self.children[1].evaluate(st)
        end_val = self.children[2].evaluate(st)

        if start_val.type != "number" or end_val.type != "number":
            raise Exception("[Semantic] error code")

        st.set_value(var_name, start_val)

        while st.get_value(var_name).value <= end_val.value:
            res = self.children[3].evaluate(st)

            if isinstance(res, tuple) and res[0] == "return":
                return res

            atual = st.get_value(var_name)
            st.set_value(var_name, Variable("number", atual.value + 1))

        return None

    def generate(self, st):
        pass

class Read(Node):
     def __init__(self, value, children):
        super().__init__(value, children)

     def evaluate(self, st):
        try:
            return Variable("number", int(input()))
        except ValueError:
            raise Exception("[Semantic] error code")
     def generate(self, st):
         Code.append("  push scan_int ; endereço de memória de suporte")
         Code.append("  push format_in ; formato de entrada (int)")
         Code.append("  call scanf")
         Code.append("  add esp, 8 ; Remove os argumentos da pilha")
         Code.append("  mov eax, dword [scan_int] ; retorna o valor lido em EAX")


class Block(Node):
    def __init__(self, value: str, children: list["Node"]):
        super().__init__(value, children)
    def evaluate(self, st):
         current_st = st

         if self.value != "program":
            current_st = SymbolTable(st)

         for child in self.children:
            res = child.evaluate(current_st)

            if isinstance(res, tuple) and res[0] == "return":
               return res

         return None
    def generate(self, st):
        for child in self.children:
            child.generate(st)


class NoOp(Node):
    def __init__(self, value, children):
        super().__init__(value, children)

    def evaluate(self, st):
        return None
    
    def generate(self, st):
        pass



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
       elif caracter == ",":
            self.next = Token("COMMA", ',')
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
       elif caracter == ".":
         if self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "..":
           self.next = Token("CONCAT", "..")
           self.position += 2
         else:
            raise Exception("[Lexer] error code")
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
                   raise Exception("[Lexer] error code")
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
            elif ident == "function":
                self.next = Token("FUNC", ident)
            elif ident == "return":
                self.next = Token("RETURN", ident)
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
            elif ident == "imut":
                  self.next = Token("IMUT", ident)
            elif ident == "for":
                  self.next = Token("FOR", ident)
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

        if Parser.lexer.next.kind == "IF":
           Parser.lexer.select_next()

           cond = Parser.parse_bool_expression()

           if Parser.lexer.next.kind != "OPEN_IF_BRA":  # then
              raise Exception("[Parser] error code")

           Parser.lexer.select_next()
           true_expr = Parser.parse_bool_expression()

           if Parser.lexer.next.kind != "ELSE":
             raise Exception("[Parser] error code")

           Parser.lexer.select_next()
           false_expr = Parser.parse_bool_expression()

           if Parser.lexer.next.kind != "CLOSE_BRA":  # end
             raise Exception("[Parser] error code")

           Parser.lexer.select_next()

           return IfExpr("ifexpr", [cond, true_expr, false_expr])
        if Parser.lexer.next.kind == "INT":
            res = IntVal(int(Parser.lexer.next.value), [])
            Parser.lexer.select_next()
            return res
        elif Parser.lexer.next.kind == "IDEN":
            ident_name = Parser.lexer.next.value
            Parser.lexer.select_next()

            if Parser.lexer.next.kind  == "OPEN_PAR":
                Parser.lexer.select_next()

                args = []

                if Parser.lexer.next.kind != "CLOSE_PAR":
                    while True:
                        args.append(Parser.parse_bool_expression())

                        if Parser.lexer.next.kind == "COMMA":
                            Parser.lexer.select_next()
                        else:
                            break
                
                if Parser.lexer.next.kind != "CLOSE_PAR":
                    raise Exception("[Parser] error code")
                Parser.lexer.select_next()
                return FuncCall(ident_name, args)
            else:
                return Identifier(ident_name, [])
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

             while Parser.lexer.next.kind in ("PLUS", "MINUS", "CONCAT"):
                op = Parser.lexer.next.kind
                Parser.lexer.select_next()

                if op == "PLUS":
                   res = BinOp("+", [res, Parser.parse_term()])
                elif op == "MINUS":
                    res = BinOp("-", [res, Parser.parse_term()])
                elif op == "CONCAT":
                    res = BinOp("..", [res, Parser.parse_term()])

             return res


    @staticmethod
    def parse_statement():

        if Parser.lexer.next.kind in ("VAR", "IMUT"):
            return Parser.parse_var_declaration()
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
            elif Parser.lexer.next.kind == "OPEN_PAR":
                Parser.lexer.select_next()
                args = []
                if Parser.lexer.next.kind != "CLOSE_PAR":
                    while True:
                        args.append(Parser.parse_bool_expression())
                        
                        if Parser.lexer.next.kind == "COMMA":
                            Parser.lexer.select_next()
                        else:
                            break
                if Parser.lexer.next.kind != "CLOSE_PAR":
                     raise Exception("[Parser] error code")
                
                Parser.lexer.select_next()

                if Parser.lexer.next.kind == "END":
                    Parser.lexer.select_next()
                    return FuncCall(ident.value, args)
                elif Parser.lexer.next.kind == "EOF":
                    return FuncCall(ident.value, args)
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
        elif Parser.lexer.next.kind == "FOR":
          Parser.lexer.select_next()

          if Parser.lexer.next.kind != "IDEN":
            raise Exception("[Parser] error code")

          ident = Identifier(Parser.lexer.next.value, [])
          Parser.lexer.select_next()

          if Parser.lexer.next.kind != "ASSIGN":
            raise Exception("[Parser] error code")

          Parser.lexer.select_next()
          start_expr = Parser.parse_bool_expression()

          if Parser.lexer.next.kind != "COMMA":
             raise Exception("[Parser] error code")

          Parser.lexer.select_next()
          end_expr = Parser.parse_bool_expression()

          if Parser.lexer.next.kind != "OPEN_BRA":  # do
            raise Exception("[Parser] error code")

          Parser.lexer.select_next()

          children = []

          while Parser.lexer.next.kind != "CLOSE_BRA":
            stmt = Parser.parse_statement()
            if stmt is not None:
               children.append(stmt)

          Parser.lexer.select_next()

          return For("for", [ident, start_expr, end_expr, Block("block", children)])
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
        elif Parser.lexer.next.kind == "RETURN":
            Parser.lexer.select_next()
            expr = Parser.parse_bool_expression()
            if Parser.lexer.next.kind == "END":
                Parser.lexer.select_next()
                return Return("return", [expr])
            elif Parser.lexer.next.kind == "EOF":
                return Return("return", [expr])
            else:
                 raise Exception("[Parser] error code")
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
    def parse_var_declaration():

      is_immutable = Parser.lexer.next.kind == "IMUT"

      Parser.lexer.select_next()

      if Parser.lexer.next.kind != "IDEN":
          raise Exception("[Parser] error code")

      ident = Identifier(Parser.lexer.next.value, [])
      Parser.lexer.select_next()

      children = [ident]

      if is_immutable:
       if Parser.lexer.next.kind != "ASSIGN":
           raise Exception("[Parser] error code")

       Parser.lexer.select_next()
       children.append(Parser.parse_bool_expression())

       if Parser.lexer.next.kind == "END":
          Parser.lexer.select_next()
          return VarDec(None, children, True)
       elif Parser.lexer.next.kind == "EOF":
          return VarDec(None, children, True)

       raise Exception("[Parser] error code")

      if Parser.lexer.next.kind != "TYPE":
       raise Exception("[Parser] error code")

      vtype = Parser.lexer.next.value
      Parser.lexer.select_next()

      if Parser.lexer.next.kind == "ASSIGN":
        Parser.lexer.select_next()
        children.append(Parser.parse_bool_expression())

      if Parser.lexer.next.kind == "END":
        Parser.lexer.select_next()
        return VarDec(vtype, children, False)
      elif Parser.lexer.next.kind == "EOF":
         return VarDec(vtype, children, False)

      raise Exception("[Parser] error code")
    
    @staticmethod
    def parse_func_declaration():
        if Parser.lexer.next.kind !=  "FUNC":
            raise Exception("[Parser] error code")
        Parser.lexer.select_next()
        if Parser.lexer.next.kind != "IDEN":
            raise Exception("[Parser] error code")
        func_name = Identifier(Parser.lexer.next.value, [])
        Parser.lexer.select_next()

        if Parser.lexer.next.kind != "OPEN_PAR":
          raise Exception("[Parser] error code")
        Parser.lexer.select_next()

        params = []

        if Parser.lexer.next.kind != "CLOSE_PAR":
            while True:
                if Parser.lexer.next.kind != "IDEN":
                     raise Exception("[Parser] error code")
                param_name = Identifier(Parser.lexer.next.value, [])
                Parser.lexer.select_next()
                if Parser.lexer.next.kind != "TYPE":
                    raise Exception("[Parser] error code")
                param_type = Parser.lexer.next.value
                Parser.lexer.select_next()
                params.append(VarDec(param_type, [param_name]))
                if Parser.lexer.next.kind == "COMMA":
                    Parser.lexer.select_next()
                else:
                    break

        if Parser.lexer.next.kind != "CLOSE_PAR":
             raise Exception("[Parser] error code")
        Parser.lexer.select_next()
        
        if Parser.lexer.next.kind == "TYPE":
            return_type = Parser.lexer.next.value
            Parser.lexer.select_next()
        else:
            return_type = "void"
        body = []
        
        while Parser.lexer.next.kind != "CLOSE_BRA":
            stmt = Parser.parse_statement()
            if stmt is not None:
                body.append(stmt)

        Parser.lexer.select_next()
        return FuncDec(return_type, [func_name] + params + [Block("block", body)])
   
    @staticmethod
    def parse_program():
         children = []
         while Parser.lexer.next.kind != "EOF":
             if Parser.lexer.next.kind == "FUNC":
                 stmt = Parser.parse_func_declaration()
             else:
                 stmt = Parser.parse_statement()
             children.append(stmt)
         return Block("program", children)

    @staticmethod
    def run(code):
        Parser.lexer = Lexer(code, 0)
        Parser.lexer.select_next()
        res = Parser.parse_program()

        if Parser.lexer.next.kind != "EOF":
           raise Exception("[Parser] error code")

        res.evaluate(Parser.symbol_table)   # checagem semântica
        return res                          # ret

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.lua")
        sys.exit(1)

    arquivo = sys.argv[1]

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo}' não encontrado.")
        sys.exit(1)

    codigo = PrePro.filter(codigo)

    Parser.symbol_table = SymbolTable()
    Code.instructions = []
    Node.id = 0

    ast = Parser.run(codigo)
    ast.generate(Parser.symbol_table)

    saida = os.path.splitext(arquivo)[0] + ".asm"
    Code.dump(saida)

    #print(f"Arquivo gerado: {saida}")


if __name__ == "__main__":
    main()