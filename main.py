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

# Inicializar servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# Segurança e hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Banco de dados fictício para autenticação
fake_users_db = {
    "user1": {"username": "user1", "password": pwd_context.hash("password1")},
    "user2": {"username": "user2", "password": pwd_context.hash("password2")}
}

# Modelo de dados
class SenhaBase(BaseModel):
    id: int
    nome: str
    senha: str
    base: Optional[str] = None
    data_criacao: str

class SenhaCreate(BaseModel):
    nome: str
    base: Optional[str]
    total_chars: int

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
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            base TEXT,
            data_criacao TEXT NOT NULL,
            usuario TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Funções de autenticação
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
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

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user})
    return {"access_token": access_token, "token_type": "bearer"}

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
    cursor.execute("INSERT INTO senhas (nome, senha, base, data_criacao, usuario) VALUES (?, ?, ?, ?, ?)",
                   (senha_data.nome, senha, base, data_criacao, current_user))
    conn.commit()
    conn.close()

    return SenhaBase(id=cursor.lastrowid, nome=senha_data.nome, senha=senha, base=base, data_criacao=data_criacao)

@app.get("/senhas/", response_model=List[SenhaBase])
def listar_senhas(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, senha, base, data_criacao FROM senhas WHERE usuario = ?", (current_user,))
    rows = cursor.fetchall()
    conn.close()

    return [SenhaBase(id=row["id"], nome=row["nome"], senha=row["senha"], base=row["base"], data_criacao=row["data_criacao"]) for row in rows]

@app.get("/senhas/{senha_id}", response_model=SenhaBase)
def get_senha(senha_id: int, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, senha, base, data_criacao FROM senhas WHERE id = ? AND usuario = ?", (senha_id, current_user))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Senha não encontrada")

    return SenhaBase(id=row["id"], nome=row["nome"], senha=row["senha"], base=row["base"], data_criacao=row["data_criacao"])

@app.delete("/senhas/{senha_id}")
def delete_senha(senha_id: int, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas WHERE id = ? AND usuario = ?", (senha_id, current_user))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Senha não encontrada")

    return {"message": "Senha deletada com sucesso."}

@app.delete("/senhas/")
def apagar_todas_senhas(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas WHERE usuario = ?", (current_user,))
    conn.commit()
    conn.close()
    return {"message": "Todas as senhas foram apagadas."}
