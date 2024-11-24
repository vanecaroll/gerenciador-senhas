import os
import sqlite3
import json
import secrets
import string
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

class PassGen:
    def __init__(self):
        # Conectar ao banco de dados SQLite
        db_path = os.getenv("DB_PATH", "senhas.db")  # Caminho do BD vindo da variável de ambiente
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

        # Carregar mapeamento de substituição de caracteres
        self.char_map = json.loads(os.getenv("CHAR_MAP", "{}"))

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

    def gerar_senha(self, base, total_chars):
        if base:
            # Utiliza o mapeamento para substituir caracteres
            senha = "".join(self.char_map.get(letra, letra) for letra in base)
        else:
            # Gera senha aleatória
            alfanumerico = string.ascii_letters + string.digits
            senha = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))

        # Salvar senha no banco de dados
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO senhas (senha, base, data_criacao) VALUES (?, ?, ?)", (senha, base, data_criacao))
        self.conn.commit()
        return senha


pass_gen = PassGen()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/nova-senha')
def nova_senha():
    return render_template('nova-senha.html')

@app.route('/gerar-senha', methods=['POST'])
def gerar_senha():
    base = request.form.get('base', '').strip()
    quantidade = int(request.form.get('quantidade', 10))

    senha = pass_gen.gerar_senha(base, quantidade)

    # Após gerar a senha, redirecionar para a tela de listagem
    return redirect(url_for('listar_senhas'))

@app.route('/listar-senhas')
def listar_senhas():
    pass_gen.cursor.execute("SELECT * FROM senhas ORDER BY id DESC")
    registros = pass_gen.cursor.fetchall()
    return render_template('listagem-senhas.html', registros=registros)

if __name__ == '__main__':
    app.run(debug=True)
