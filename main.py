import sys
import re

class Token:
     def __init__(self, kind, value):
          self.kind = kind
          self.value = value

class Lexer:
     def __init__(self, source, position):
          self.source = source
          self.position = position
          self.next = None
     def selectNext(self):
        # Pular espaços
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position += 1

        # Se chegou ao fim da string
        if self.position >= len(self.source):
            self.next = Token("EOF", '')
            return

        caracter = self.source[self.position]

        # Identificar operadores
        if caracter == "+":
            self.next = Token("PLUS", '+')
            self.position += 1
        elif caracter == "-":
            self.next = Token("MINUS", '-')
            self.position += 1
        elif caracter.isdigit():
            # Ler número
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("INT", num)
        else:
            # Se encontrou caractere inválido (nem número, nem operador, nem espaço)
            raise Exception(f"Caractere inválido encontrado: '{caracter}' na posição {self.position}")

class Parser:
     @staticmethod
     def parseExpression(lex):
          if lex.next.kind != "INT":
               raise Exception("ERRO")
          res = int(lex.next.value)
          lex.selectNext()
          while(lex.next.kind == "PLUS" or lex.next.kind == "MINUS"):
               op = lex.next.kind 
               lex.selectNext()
               if lex.next.kind != "INT":
                    raise Exception("ERRO")
               if op == "PLUS":
                    res += int(lex.next.value)
               elif op == "MINUS":
                    res -= int(lex.next.value)
               lex.selectNext()
          return res
     @staticmethod
     def run(code):
          lex = Lexer(code, 0)
          lex.selectNext()
          par = Parser.parseExpression(lex)
          res = Parser.parseExpression(lex)
          if (lex.next.kind != "EOF"):
              raise Exception("expressão invalida")
          else:
              return Parser.parseExpression(lex)
              return res



def main():
     if len(sys.argv) != 2:
        print("Uso: python3 main.py 'expressão'")
        sys.exit(1)

     print(Parser.run(sys.argv[1]))


if __name__ == "__main__":
    main()