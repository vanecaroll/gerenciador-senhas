import os
import sqlite3
import json
import PySimpleGUI as sg
import secrets
import string
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class PassGen:
    def __init__(self):
        # Conectar ao banco de dados SQLite
        db_path = os.getenv("DB_PATH", "senhas.db")  # caminho do BD vindo da variável de ambiente
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

        # Carregar mapeamento de substituição de caracteres
        self.char_map = json.loads(os.getenv("CHAR_MAP", "{}"))

        # Layout do GUI
        sg.theme('Black')
        layout = [
            [sg.Text('Base da Senha', size=(15, 1)), sg.Input(key='base', size=(20, 1))],
            [sg.Text('Quantidade de caracteres'), sg.Combo(values=list(range(1, 31)), key='total_chars', default_value=10, size=(3, 1))],
            [sg.Button('Gerar Senha'), sg.Button('Listar Senhas'), sg.Button('Apagar Todas')],
            [sg.Output(size=(32, 5))]
        ]
        # Declarar janela
        self.janela = sg.Window('Password Generator', layout)

    def criar_tabela(self):
        # Criar tabela para armazenar as senhas, se não existir
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS senhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                senha TEXT NOT NULL,
                base TEXT,
                data_criacao TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def Iniciar(self):
        while True:
            evento, valores = self.janela.read()
            if evento == sg.WINDOW_CLOSED:
                break
            elif evento == 'Gerar Senha':
                self.gerar_senha(valores)
            elif evento == 'Listar Senhas':
                self.listar_senhas_gui()
            elif evento == 'Apagar Todas':
                self.apagar_todas_senhas()

    def gerar_senha(self, valores):
        base = valores['base']
        total_chars = int(valores['total_chars'])

        if base:  
            # Utiliza o mapeamento para substituir caracteres
            senha = "".join(self.char_map.get(letra, letra) for letra in base)
            print("Senha gerada a partir da base: ", senha)
        else:
            alfanumerico = string.ascii_letters + string.digits
            senha = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))
            print("Senha gerada automaticamente: ", senha)
        
        # Salvar senha no banco de dados
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO senhas (senha, base, data_criacao) VALUES (?, ?, ?)", (senha, base, data_criacao))
        self.conn.commit()

    def listar_senhas_gui(self):
        # Executa uma consulta para obter as senhas salvas
        self.cursor.execute("SELECT * FROM senhas")
        registros = self.cursor.fetchall()
        
        # Layout da nova janela para exibir as senhas
        layout = [[sg.Text("ID | Senha | Base | Data de Criação")]]
        for registro in registros:
            layout.append([sg.Text(f"{registro[0]} | {registro[1]} | {registro[2]} | {registro[3]}")])
        
        # Cria e abre a nova janela com a lista de senhas
        janela_listagem = sg.Window('Senhas Salvas', layout)
        janela_listagem.read(close=True)

    def apagar_todas_senhas(self):
        # Confirmação para apagar todas as senhas
        confirmacao = sg.popup_yes_no("Tem certeza que deseja apagar todas as senhas?")
        if confirmacao == "Yes":
            self.cursor.execute("DELETE FROM senhas")
            self.conn.commit()
            sg.popup("Todas as senhas foram apagadas.")

    def __del__(self):
        # Fechar a conexão com o banco de dados ao sair
        self.conn.close()

# Inicialização do gerador de senhas
gen = PassGen()
gen.Iniciar()
