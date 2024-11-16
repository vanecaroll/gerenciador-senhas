import os
import sqlite3
import json
import secrets
import string
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Caminho do banco de dados
db_path = os.getenv("DB_PATH", "senhas.db")  # caminho do BD vindo da variável de ambiente

# Conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para retornar os resultados como dicionários
    return conn

# Criar tabela para armazenar as senhas, se não existir
def criar_tabela():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            senha TEXT NOT NULL,
            base TEXT,
            data_criacao TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Mapeamento de substituição de caracteres
char_map = json.loads(os.getenv("CHAR_MAP", "{}"))

@app.route('/')
def index():
    return render_template('index.html')  # Página principal do frontend

@app.route('/api/senhas', methods=['GET'])
def listar_senhas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM senhas")
    senhas = cursor.fetchall()
    conn.close()
    return jsonify([dict(senha) for senha in senhas])  # Retorna a lista de senhas como JSON

@app.route('/api/gerar_senha', methods=['POST'])
def gerar_senha():
    data = request.json
    base = data.get('base', '')
    total_chars = data.get('total_chars', 10)

    if base:
        senha = "".join(char_map.get(letra, letra) for letra in base)
    else:
        alfanumerico = string.ascii_letters + string.digits
        senha = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))

    # Salvar a senha no banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()
    data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO senhas (senha, base, data_criacao) VALUES (?, ?, ?)", (senha, base, data_criacao))
    conn.commit()
    conn.close()
    
    return jsonify({"senha": senha, "base": base, "data_criacao": data_criacao})

@app.route('/api/apagar_todas_senhas', methods=['POST'])
def apagar_todas_senhas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas")
    conn.commit()
    conn.close()
    return jsonify({"message": "Todas as senhas foram apagadas."})

if __name__ == '__main__':
    criar_tabela()  # Cria a tabela no banco de dados
    app.run(debug=True)
