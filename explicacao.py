# Importações e Carregamento de Variáveis de Ambiente

# As bibliotecas abaixo são necessárias para o funcionamento do gerador de senhas
import os            # permite manipular variáveis de ambiente e caminhos de arquivos
import sqlite3       # módulo para interagir com o banco de dados SQLite
import json          # usado para interpretar o mapeamento de caracteres a partir de um arquivo .env
import PySimpleGUI as sg  # cria uma interface gráfica para o usuário (GUI)
import secrets       # gera senhas aleatórias seguras
import string        # contém caracteres pré-definidos (como letras e dígitos)
from datetime import datetime  # adiciona a data de criação da senha
from dotenv import load_dotenv  # carrega as variáveis de ambiente do arquivo .env

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Classe `PassGen` e Conexão com o Banco de Dados
class PassGen:
    def __init__(self):
        # `db_path` é o caminho para o banco de dados, carregado da variável de ambiente `DB_PATH`
        # Se não estiver definido, usa `senhas.db` como padrão.
        db_path = os.getenv("DB_PATH", "senhas.db")
        
        # `self.conn` estabelece a conexão com o banco de dados
        self.conn = sqlite3.connect(db_path)
        
        # `self.cursor` permite executar comandos SQL
        self.cursor = self.conn.cursor()
        
        # `self.criar_tabela()` chama o método para criar a tabela no banco de dados se ela ainda não existir
        self.criar_tabela()

        # Carregar o Mapeamento de Substituição de Caracteres
        # `self.char_map` carrega um mapeamento de caracteres definido em `CHAR_MAP`
        # Isso permite substituir caracteres automaticamente durante a geração da senha
        self.char_map = json.loads(os.getenv("CHAR_MAP", "{}"))

        # Layout da Interface com PySimpleGUI
        # O layout define a estrutura da interface:
        # - Campo para inserir uma base de senha (`base`)
        # - Combo box para selecionar a quantidade de caracteres (`total_chars`)
        # - Botões `Gerar Senha` e `Excluir Todas`
        # - Área de output para exibir a senha gerada
        sg.theme('Black')
        layout = [
            [sg.Text('Base da Senha', size=(15, 1)), sg.Input(key='base', size=(20, 1))],
            [sg.Text('Quantidade de caracteres'), sg.Combo(values=list(range(1, 31)), key='total_chars', default_value=10, size=(3, 1))],
            [sg.Button('Gerar Senha'), sg.Button('Excluir Todas')],
            [sg.Output(size=(32, 5))]
        ]
        self.janela = sg.Window('Password Generator', layout)

    # Criar a Tabela de Senhas
    def criar_tabela(self):
        # O método `criar_tabela()` cria a tabela `senhas` no banco de dados, se ainda não existir,
        # com colunas para `id`, `senha`, `base`, e `data_criacao`
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS senhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                senha TEXT NOT NULL,
                base TEXT,
                data_criacao TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # Método Principal `Iniciar`
    def Iniciar(self):
        # O método `Iniciar` é o loop principal, que lê eventos e valores da interface.
        # - Se o botão `Gerar Senha` é clicado, chama o método `gerar_senha()`
        # - Se o botão `Excluir Todas` é clicado, chama o método `excluir_todas_senhas()`
        while True:
            evento, valores = self.janela.read()
            if evento == sg.WINDOW_CLOSED:
                break
            elif evento == 'Gerar Senha':
                self.gerar_senha(valores)
            elif evento == 'Excluir Todas':
                self.excluir_todas_senhas()

    # Gerar Senha com Base no Mapeamento de Caracteres
    def gerar_senha(self, valores):
        # O método `gerar_senha` verifica se o usuário inseriu uma base de senha personalizada.
        base = valores['base']
        total_chars = int(valores['total_chars'])

        # Se a base for fornecida, utiliza o mapeamento para substituir caracteres
        if base:  
            senha = "".join(self.char_map.get(letra, letra) for letra in base)
            print("Senha gerada a partir da base: ", senha)
        else:
            # Caso contrário, gera uma senha aleatória usando letras e dígitos
            alfanumerico = string.ascii_letters + string.digits
            senha = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))
            print("Senha gerada automaticamente: ", senha)
        
        # Salvar Senha no Banco de Dados
        # A senha gerada, a base (caso fornecida) e a data de criação são salvas no banco de dados
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO senhas (senha, base, data_criacao) VALUES (?, ?, ?)", (senha, base, data_criacao))
        self.conn.commit()

    # Excluir Todas as Senhas
    def excluir_todas_senhas(self):
        # O método `excluir_todas_senhas` remove todas as senhas da tabela `senhas` e imprime uma confirmação
        self.cursor.execute("DELETE FROM senhas")
        self.conn.commit()
        print("Todas as senhas foram excluídas.")

    # Fechar a Conexão ao Final
    def __del__(self):
        # O método `__del__` fecha a conexão com o banco de dados quando o objeto `PassGen` é destruído
        self.conn.close()

# Inicializar o Gerador de Senhas
# Aqui, cria-se uma instância de `PassGen` e chama o método `Iniciar` para iniciar o loop de execução da interface
gen = PassGen()
gen.Iniciar()

# Arquivo `.env`
# Um exemplo do conteúdo que o arquivo `.env` deve conter:
#
# DB_PATH=senhas.db
# CHAR_MAP={"A": "5", "B": "*", "C": "2", "D": "F", "E": "4", "F": "3", "R": "A", "S": "%", "M": "$", "N": "Q"}
#
# - `DB_PATH` define o caminho do banco de dados SQLite.
# - `CHAR_MAP` é um dicionário JSON para substituir caracteres específicos durante a geração da senha.
# 
# Esse arquivo `.env` facilita a personalização do caminho do banco de dados e dos caracteres, tornando o projeto mais prático e seguro.
