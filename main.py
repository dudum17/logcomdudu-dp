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
    def parse_factor():
      if Parser.lexer.next.kind == "INT":
        res = Parser.lexer.next.value   # <-- era Parser.lex
        Parser.lexer.select_next()
        return int(res)

      elif Parser.lexer.next.kind == "PLUS":
        Parser.lexer.select_next()
        return Parser.parse_factor()

      elif Parser.lexer.next.kind == "MINUS":
        Parser.lexer.select_next()
        return -Parser.parse_factor()

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
    def parse_term():
        res = Parser.parse_factor()
        while Parser.lexer.next.kind in ("MULT", "DIV"):
            op = Parser.lexer.next.kind
            Parser.lexer.select_next()
            if op == "MULT":
                 res *= Parser.parse_factor()
            elif op == "DIV":
                 res //= Parser.parse_factor()
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
        res =  Parser.parse_expression()
        if Parser.lexer.next.kind != "EOF":
          raise Exception(f"expressão invalida, sobrou token: {Parser.lexer.next.kind}")
        return res

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py \"expressão\"")
        sys.exit(1)

    # NÃO captura exception: o tester quer ver a Exception acontecer
    print(Parser.run(sys.argv[1]))

if __name__ == "__main__":
    main()