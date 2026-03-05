import sys

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

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
           if self.position + 1 < len(self.source) and self.source[self.position + 1] == '*':
              self.next = Token("POWER", '**')
              self.position += 2
           else:
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
    lexer = None  # atributo estático


    @staticmethod
    def parse_atom():
      if Parser.lexer.next.kind == "INT":
        res = int(Parser.lexer.next.value)
        Parser.lexer.select_next()
        return res

      elif Parser.lexer.next.kind == "OPEN_PAR":
        Parser.lexer.select_next()
        res = Parser.parse_expression()

        if Parser.lexer.next.kind != "CLOSE_PAR":
            raise Exception("expressão invalida")

        Parser.lexer.select_next()
        return res

      else:
        raise Exception("expressão invalida")
      
    @staticmethod
    def parse_power():
    # power := atom (POWER power)?
       res = Parser.parse_atom()

       if Parser.lexer.next.kind == "POWER":
        Parser.lexer.select_next()
        expo = Parser.parse_power()  # associativo à direita
        res = res ** expo

       return res

    @staticmethod
    def parse_factor():
        # factor := (PLUS factor) | (MINUS factor) | power

       if Parser.lexer.next.kind == "PLUS":
          Parser.lexer.select_next()
          return Parser.parse_factor()

       elif Parser.lexer.next.kind == "MINUS":
          Parser.lexer.select_next()
          return -Parser.parse_factor()

       return Parser.parse_power()

    @staticmethod
    def parse_term():
        res = Parser.parse_factor()

        while Parser.lexer.next.kind in ("MULT", "DIV"):
            op = Parser.lexer.next.kind
            Parser.lexer.select_next()

            rhs = Parser.parse_factor()

            if op == "MULT":
                res = res * rhs
            else:  # DIV
                if rhs == 0:
                    raise Exception("divisão por zero")
                res = res // rhs

        return res

    @staticmethod
    def parse_expression():
        res = Parser.parse_term()
        while Parser.lexer.next.kind in ("PLUS", "MINUS"):
            op = Parser.lexer.next.kind
            Parser.lexer.select_next()
            if op == "PLUS":
                res += Parser.parse_term()
            elif op == "MINUS":
                res -= Parser.parse_term()
        return res

    @staticmethod
    def run(code):
        Parser.lexer = Lexer(code, 0)
        Parser.lexer.select_next()
        res = Parser.parse_expression()
        if Parser.lexer.next.kind != "EOF":
            raise Exception("[Parser] error code")
        return res

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py \"expressão\"")
        sys.exit(1)

    print(Parser.run(sys.argv[1]))

if __name__ == "__main__":
    main()