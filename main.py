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

        elif caracter.isdigit():
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("INT", num)

        else:
            raise Exception(f"Caractere inválido: '{caracter}' na posição {self.position}")

class Parser:
    @staticmethod
    def parse_expression(lex):
        if lex.next.kind != "INT":
            raise Exception("ERRO")

        res = int(lex.next.value)
        lex.select_next()

        while lex.next.kind in ("PLUS", "MINUS"):
            op = lex.next.kind
            lex.select_next()

            if lex.next.kind != "INT":
                raise Exception("ERRO")

            if op == "PLUS":
                res += int(lex.next.value)
            else:  # MINUS
                res -= int(lex.next.value)

            lex.select_next()

        return res

    @staticmethod
    def run(code):
        lex = Lexer(code, 0)
        lex.select_next()
        res = Parser.parse_expression(lex)
        if lex.next.kind != "EOF":
            raise Exception("expressão invalida")
        return res

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py \"expressão\"")
        sys.exit(1)

    print(Parser.run(sys.argv[1]))

if __name__ == "__main__":
    main()