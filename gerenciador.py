import PySimpleGUI as sg
import secrets
import string

class PassGen:
    def __init__(self):
        # Layout
        sg.theme('Black')
        layout = [
            [sg.Text('Base da Senha', size=(15, 1)), sg.Input(key='base', size=(20, 1))],
            [sg.Text('Quantidade de caracteres'), sg.Combo(values=list(range(0, 31)), key='total_chars', default_value=0, size=(3, 1))],
            [sg.Button('Gerar Senha')],
            [sg.Output(size=(32, 5))]
        ]
        # Declarar janela
        self.janela = sg.Window('Password Generator', layout)

    def Iniciar(self):
        while True:
            evento, valores = self.janela.read()
            if evento == sg.WINDOW_CLOSED:
                break
            elif evento == 'Gerar Senha':
                self.gerar_senha(valores)

    def gerar_senha(self, valores):
        base = valores['base']
        total_chars = valores['total_chars']

        # Gera senha aleatória somente se a base estiver vazia e total_chars for 0
        if not base and total_chars == 0:
            alfanumerico = string.ascii_letters + string.digits
            senha_gerada = "".join(secrets.choice(alfanumerico) for _ in range(10))  # Senha aleatória de 10 caracteres
            print("Senha gerada automaticamente: ", senha_gerada)
        elif len(base) > 1:  
            # Gera a senha de acordo com a base
            """
            Security = chave
            5ecur1ty = senha
            """
            senha = ""
            for letra in base:
                if letra in "Aa": senha += "5"
                elif letra in "Bb": senha += "*"
                elif letra in "Cc": senha += "2"
                elif letra in "Dd": senha += "F"
                elif letra in "Ee": senha += "4"
                elif letra in "Ff": senha += "3"
                elif letra in "Rr": senha += "A"
                elif letra in "Ss": senha += "%"
                elif letra in "Mm": senha += "$"
                elif letra in "Nn": senha += "Q"
                elif letra in "Ll": senha += "O"
                elif letra in "Oo": senha += "G"
                elif letra in "1": senha += "T"
                elif letra in "2": senha += "#"
                elif letra in "3": senha += "W"
                elif letra in "4": senha += "H"
                elif letra in "5": senha += "0"
                elif letra in "6": senha += "C"
                elif letra in "7": senha += "Y"
                elif letra in "8": senha += "F"
                else: senha += letra
            
            print("Senha gerada a partir da base: ", senha)
        elif total_chars > 0:  # Gera uma senha aleatória se apenas a base estiver vazia
            alfanumerico = string.ascii_letters + string.digits
            senha_gerada = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))
            print("Senha gerada automaticamente: ", senha_gerada)

gen = PassGen()
gen.Iniciar()




