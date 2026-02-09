import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py 'expressão'")
        sys.exit(1)

    expressao = sys.argv[1]  # pega o argumento passado    

    padrao = r"^\s*\d+\s*([+-]\s*\d+\s*)*$"

    if not re.fullmatch(padrao, expressao):
        print("Erro: expressão inválida", file=sys.stderr)
        sys.exit(1)
    
    try:  
        num = ""
        expr = ""
        sum = 0
        for i in expressao:
            if i != " ":
                if (i != "+") and (i != "-"):
                    num += i
                elif (i == "+"):
                    num = int(num)
                    if expr != "-":
                        sum += num
                    else:
                        sum -= num
                    expr = "+"
                    num = ""
                elif (i == "-"):
                    num = int(num)
                    if expr != "-":
                        sum += num
                    else:
                        sum -= num
                    expr = "-"
                    num = ""

        if num:
            num = int(num)
            if expr == "+":
                sum += num
            else:
                sum -= num
        print(sum)                     
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()