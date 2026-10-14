from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# Parâmetros da configuração da conexão
user =  os.getenv('user')
senha = os.getenv('senha')
host = os.getenv('host')
porta = os.getenv('porta')
banco = os.getenv('banco')

# Conexão
DATABASE_URL = f'postgresql+psycopg://{user}:{senha}@{host}:{porta}/{banco}'

# Engine de conexão com o banco de dados
engine = create_engine(DATABASE_URL)

# Configuração de sessão
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
  pass

def get_db():
  with SessionLocal() as db:
    yield db