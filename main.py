import os
import sqlite3
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Configurações do JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Inicialização da FastAPI
app = FastAPI()

# Segurança e hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Banco de dados SQLite
DB_PATH = "senhas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            senha TEXT NOT NULL,
            base TEXT,
            data_criacao TEXT NOT NULL,
            usuario TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Modelo de dados
class SenhaBase(BaseModel):
    senha: str
    base: Optional[str] = None
    data_criacao: str

class SenhaCreate(BaseModel):
    base: Optional[str]
    total_chars: int

# Funções de autenticação
def authenticate_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not pwd_context.verify(password, user[0]):
        return None
    return username

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints

# Rota para login
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user})
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para cadastro de usuários
@app.post("/register")
def registrar_usuario(username: str, password: str):
    hashed_password = pwd_context.hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuarios (username, hashed_password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    
    conn.close()
    return {"message": "Usuário registrado com sucesso!"}

# Rota para criação de senhas
@app.post("/senhas/", response_model=SenhaBase)
def criar_senha(senha_data: SenhaCreate, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Gerar senha
    base = senha_data.base
    total_chars = senha_data.total_chars
    char_map = json.loads(os.getenv("CHAR_MAP", "{}"))

    if base:
        senha = "".join(char_map.get(letra, letra) for letra in base)
    else:
        import secrets, string
        alfanumerico = string.ascii_letters + string.digits
        senha = "".join(secrets.choice(alfanumerico) for _ in range(total_chars))

    data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Inserir no banco
    cursor.execute("INSERT INTO senhas (senha, base, data_criacao, usuario) VALUES (?, ?, ?, ?)",
                   (senha, base, data_criacao, current_user))
    conn.commit()
    conn.close()

    return SenhaBase(senha=senha, base=base, data_criacao=data_criacao)

# Rota para listar senhas
@app.get("/senhas/", response_model=List[SenhaBase])
def listar_senhas(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT senha, base, data_criacao FROM senhas WHERE usuario = ?", (current_user,))
    rows = cursor.fetchall()
    conn.close()

    return [SenhaBase(senha=row["senha"], base=row["base"], data_criacao=row["data_criacao"]) for row in rows]

# Rota para deletar todas as senhas
@app.delete("/senhas/")
def apagar_todas_senhas(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas WHERE usuario = ?", (current_user,))
    conn.commit()
    conn.close()
    return {"message": "Todas as senhas foram apagadas."}
