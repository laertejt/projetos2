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



from sqlalchemy import URL

MYSQL_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ["MYSQL_HOST"],
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.environ["MYSQL_DATABASE"],
    query={"charset": "utf8mb4"},
)

mysql_engine = create_engine(MYSQL_URL, pool_pre_ping=True)

MySQLSessionLocal = sessionmaker(bind=mysql_engine)


class MySQLBase(DeclarativeBase):
    pass


def get_mysql_db():
    with MySQLSessionLocal() as db:
        yield db