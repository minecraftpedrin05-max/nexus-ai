from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./usuarios.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    nome = Column(String)
    mensagens_usadas = Column(Integer, default=0)
    ultimo_reset = Column(DateTime, default=datetime.now)
    metodo_login = Column(String)
    codigo_verificacao = Column(String, nullable=True)
    verificado = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

class LoginRequest(BaseModel):
    email: str
    nome: str
    metodo: str

class ChatRequest(BaseModel):
    email: str
    mensagem: str
    tipo: str

@app.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    
    if not usuario:
        usuario = Usuario(
            email=request.email,
            nome=request.nome,
            metodo_login=request.metodo,
            verificado=1
        )
        db.add(usuario)
        db.commit()
    
    return {"status": "logado", "usuario": usuario.nome}

@app.post("/chat")
def chat(request: ChatRequest):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    if usuario.mensagens_usadas >= 200:
        tempo_espera = 20 if request.tipo == "facil" else 180
        proximo_reset = usuario.ultimo_reset + timedelta(minutes=tempo_espera)
        
        if datetime.now() < proximo_reset:
            tempo_falta = (proximo_reset - datetime.now()).total_seconds() / 60
            return {
                "status": "limite_atingido",
                "tempo_espera_minutos": int(tempo_falta)
            }
        else:
            usuario.mensagens_usadas = 0
            usuario.ultimo_reset = datetime.now()
    
    usuario.mensagens_usadas += 1
    db.commit()
    
    resposta = f"Você perguntou: {request.mensagem}"
    
    return {
        "status": "sucesso",
        "resposta": resposta,
        "mensagens_restantes": 200 - usuario.mensagens_usadas
    }

@app.get("/info")
def info(email: str):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {
        "nome": usuario.nome,
        "mensagens_usadas": usuario.mensagens_usadas,
        "mensagens_restantes": 200 - usuario.mensagens_usadas,
        "metodo_login": usuario.metodo_login
  }
