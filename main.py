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
            raise Exception("[Lexer] error code")

class Parser:
    lexer = None  # atributo estático


    @staticmethod
    def parse_expression():
        # expressão deve começar com INT
        if Parser.lexer.next.kind != "INT":
            raise Exception("[Parser] error code")

        res = int(Parser.lexer.next.value)
        Parser.lexer.select_next()

        # (PLUS|MINUS INT)*
        while Parser.lexer.next.kind in ("PLUS", "MINUS"):
            op = Parser.lexer.next.kind
            Parser.lexer.select_next()

            # depois de + ou - tem que vir INT
            if Parser.lexer.next.kind != "INT":
                raise Exception("[Parser] error code")

            val = int(Parser.lexer.next.value)
            if op == "PLUS":
                res += val
            else:
                res -= val

            Parser.lexer.select_next()

        # terminou a expressão: tem que ser EOF
        if Parser.lexer.next.kind != "EOF":
            raise Exception("[Parser] error code")

        return res

    @staticmethod
    def run(code):
        Parser.lexer = Lexer(code, 0)
        Parser.lexer.select_next()
        return Parser.parse_expression()

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py \"expressão\"")
        sys.exit(1)

    # NÃO captura exception: o tester quer ver a Exception acontecer
    print(Parser.run(sys.argv[1]))

if __name__ == "__main__":
    main()