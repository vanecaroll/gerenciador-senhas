import random
import PySimpleGUI as sg
import os

class PassGen:
    def __init__(self):
# Layout
        sg.theme('Black')
        layout = [
            [sg.Text('Site/Software', size=(10,1)),
             sg.Input(key='site', size=(20,1))],
            [sg.Text('E-mail/Usuário', size=(10,1)),
              sg.Input(key='usuario', size=(20,1))],
            [sg.Text('Quantidade de caracteres'), sg.Combo(values=list(
                range(30)), key='total_chars', default_value=1, size=(3, 1))],
            [sg.Output(size=(32,5))],
            [sg.Button('Gerar Senha')]
        ]
# Declarar janela
        self.janela = sg.Window('Passwors Generator', layout)

    def Iniciar(self):
        while True:
            evento, valores = self.janela.read()
            if evento == sg.WINDOW_CLOSED:
                break

    def salvar_senha(self):
        pass

gen = PassGen()
gen.Iniciar()

# Gerenciador de Senhas

"""
Security = chave
5ecur1ty = senha

hex

1 = 1
2 = 2
até 9 = 9
10 = A
11 = B
12 = C
13 = D
14 = E
15 = F

"""

""" chave = input("Digite a base da sua senha: ")

senha = ""
for letra in chave:
    if letra in "Aa": senha = senha + "0"
    elif letra in "Bb": senha = senha + "1"
    elif letra in "Cc": senha = senha + "2"
    elif letra in "Dd": senha = senha + "3"
    elif letra in "Ee": senha = senha + "4"
    elif letra in "Ff": senha = senha + "5"
    elif letra in "Rr": senha = senha + "#"
    elif letra in "Ss": senha = senha + "%"
    elif letra in "Mm": senha = senha + "$"
    else: senha = senha + letra
print(senha) """
