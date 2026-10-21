from fastapi import APIRouter, Depends
from sqlalchemy import text
import pandas as pd
from app.database import engine, get_db
from app.schemas import AlunoIn, AlunoUpdateIn

router = APIRouter(prefix="/alunos")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "Hello, World!"}

@router.get("/pegar-dados-aluno")
def pegar_dados_alunos():
  query = "SELECT * FROM tb_alunos ORDER BY id"
  df = pd.read_sql(query, engine)
  return df.to_dict(orient="records")

@router.get("/pegar-dados-aluno-por-id/{id}")
def pegar_dados_alunos_por_id(id: int):
  query = f"SELECT * FROM tb_alunos WHERE id = {id}"
  df = pd.read_sql(query, engine)
  return df.to_dict(orient="records")

@router.post("/criar-aluno")
def criar_aluno(aluno: AlunoIn):
  # Transformando dict em df
  df = pd.DataFrame([aluno.model_dump()])
  # Insert no banco de dados
  df.to_sql("tb_alunos", engine, if_exists="append", index=False)
  return {"mensagem": "Aluno cadastrado com sucesso!"}

@router.put("/atualizar-aluno/{id}")
def atualizar_aluno(id: int, aluno: AlunoUpdateIn):
  campos_sql = ", ".join([f"{chave} = :{chave}" for chave in aluno.model_dump(exclude_unset=True).keys()])
  query = f"""
      UPDATE tb_alunos
      SET {campos_sql}
      WHERE id = :id
  """ 
  with engine.connect() as conn:
    conn.execute(
      text(query),
      {"id":id, **aluno.model_dump(exclude_unset=True)}
    )
    conn.commit(

    )
  return {"mensagem": "Aluno atualizado com sucesso."}

@router.delete("/deletar-aluno/{id}")
def deletar_aluno(id: int):
  query = f"DELETE FROM tb_alunos WHERE id = {id}"
  with engine.connect() as conn:
    conn.execute( text(query))
    conn.commit() 
  return {"mensagem": "Aluno deletado com sucesso."}

# ============================================================
# SQLALCHEMY ORM - EXEMPLOS DE OPERAÇÕES
# ============================================================
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import Session
from app.models import Aluno, Nota
# ============================================================
# 1. SELECT - BUSCAR TODOS OS REGISTROS
# ============================================================
db: Session = Depends(get_db)
stmt = select(Aluno)
alunos = db.scalars(stmt).all()
# ============================================================
# 2. SELECT COM ORDER BY
# ============================================================
stmt = select(Aluno).order_by(Aluno.id)
alunos = db.scalars(stmt).all()
# Ordenação decrescente
stmt = select(Aluno).order_by(Aluno.id.desc())
alunos = db.scalars(stmt).all()
# ============================================================
# 3. BUSCAR POR ID
# ============================================================
aluno = db.get(Aluno, 1)
# ============================================================
# 4. FILTER / WHERE
# ============================================================
stmt = select(Aluno).where(
    Aluno.nome_aluno == "Ana"
)
alunos = db.scalars(stmt).all()
# Também pode usar filter()
stmt = select(Aluno).filter(
    Aluno.nome_aluno == "Ana"
)
alunos = db.scalars(stmt).all()
# ============================================================
# 5. MÚLTIPLAS CONDIÇÕES
# ============================================================
stmt = select(Aluno).where(
    Aluno.nome_aluno == "Ana",
    Aluno.endereco_id == 1
)
alunos = db.scalars(stmt).all()
# ============================================================
# 6. OPERADORES DE FILTRO
# ============================================================
# Diferente
stmt = select(Aluno).where(
    Aluno.id != 1
)
# Maior que
stmt = select(Aluno).where(
    Aluno.id > 5
)
# Menor que
stmt = select(Aluno).where(
    Aluno.id < 10
)
# Maior ou igual
stmt = select(Aluno).where(
    Aluno.id >= 5
)
# IN
stmt = select(Aluno).where(
    Aluno.id.in_([1, 2, 3])
)
# LIKE
stmt = select(Aluno).where(
    Aluno.nome_aluno.like("%Silva%")
)
# ============================================================
# 7. LIMIT
# ============================================================
stmt = select(Aluno).limit(5)
alunos = db.scalars(stmt).all()
# ============================================================
# 8. OFFSET
# ============================================================
stmt = select(Aluno).offset(5).limit(5)
alunos = db.scalars(stmt).all()
# ============================================================
# 9. BUSCAR PRIMEIRO REGISTRO
# ============================================================
stmt = select(Aluno).where(
    Aluno.email == "ana@email.com"
)
aluno = db.scalars(stmt).first()
# ============================================================
# 10. COUNT
# ============================================================
stmt = select(func.count(Aluno.id))
total_alunos = db.scalar(stmt)
# ============================================================
# 11. AVG - MÉDIA
# ============================================================
stmt = select(func.avg(Nota.nota))
media_notas = db.scalar(stmt)
# ============================================================
# 12. MAX - MAIOR VALOR
# ============================================================
stmt = select(func.max(Nota.nota))
maior_nota = db.scalar(stmt)
# ============================================================
# 13. MIN - MENOR VALOR
# ============================================================
stmt = select(func.min(Nota.nota))
menor_nota = db.scalar(stmt)
# ============================================================
# 14. JOIN
# ============================================================
stmt = (
    select(
        Aluno.nome_aluno,
        Nota.nota
    )
    .join(
        Nota,
        Nota.aluno_id == Aluno.id
    )
)
resultado = db.execute(stmt).all()
# ============================================================
# 15. CREATE - INSERIR REGISTRO
# ============================================================
novo_aluno = Aluno(
    matricula="20260001",
    nome_aluno="Ana Silva",
    email="ana@email.com",
    endereco_id=1
)
db.add(novo_aluno)
db.commit()
# ============================================================
# 16. CREATE COM PYDANTIC
# ============================================================
novo_aluno = Aluno(
    **aluno.model_dump()
)
db.add(novo_aluno)
db.commit()
# ============================================================
# 17. REFRESH
# ===========================================================
novo_aluno = Aluno(
    matricula="20260002",
    nome_aluno="Carlos Souza",
    email="carlos@email.com",
    endereco_id=1
)
db.add(novo_aluno)
db.commit()
db.refresh(novo_aluno)
print(novo_aluno.id)
# ============================================================
# 18. UPDATE - ALTERANDO O OBJETO
# ============================================================
aluno = db.get(
    Aluno,
    1
)
aluno.nome_aluno = "Novo Nome"
db.commit()
# ============================================================
# 19. UPDATE COM SETATTR
# ============================================================
aluno_db = db.get(
    Aluno,
    1
)
dados = {
    "nome_aluno": "Maria Silva",
    "email": "maria@email.com"
}
for campo, valor in dados.items():
    setattr(
        aluno_db,
        campo,
        valor
    )
db.commit()
# ============================================================
# 20. UPDATE COM PYDANTIC
# ============================================================
aluno_db = db.get(
    Aluno,
    id
)
for campo, valor in aluno.model_dump(
    exclude_unset=True
).items():
    setattr(
        aluno_db,
        campo,
        valor
    )
db.commit()
# ============================================================
# 21. UPDATE DIRETO
# ============================================================
stmt = (
    update(Aluno)
    .where(
        Aluno.id == 1
    )
    .values(
        nome_aluno="Novo Nome"
    )
)
db.execute(stmt)
db.commit()
# ============================================================
# 22. DELETE - REMOVER OBJETO
# ============================================================
aluno = db.get(
    Aluno,
    1
)

db.delete(aluno)

db.commit()


# ============================================================
# 23. DELETE DIRETO
# ============================================================

stmt = (
    delete(Aluno)
    .where(
        Aluno.id == 10
    )
)

db.execute(stmt)

db.commit()


# ============================================================
# 24. COMMIT
# ============================================================

db.commit()


# Confirma as alterações realizadas no banco de dados.


# ============================================================
# 25. ROLLBACK
# ============================================================

db.rollback()


# Desfaz alterações da transação que ainda não foram confirmadas.


# ============================================================
# 26. EXEMPLO COM TRY / EXCEPT / ROLLBACK
# ============================================================

try:

    novo_aluno = Aluno(
        matricula="20260003",
        nome_aluno="João Silva",
        email="joao@email.com",
        endereco_id=1
    )

    db.add(novo_aluno)

    db.commit()

except Exception:

    db.rollback()

    raise


# ============================================================
# 27. EXEMPLO DE CRUD RESUMIDO
# ============================================================


# CREATE

novo_aluno = Aluno(
    matricula="20260004",
    nome_aluno="Pedro Lima",
    email="pedro@email.com",
    endereco_id=1
)

db.add(novo_aluno)

db.commit()


# READ

alunos = db.scalars(
    select(Aluno)
).all()


# READ POR ID

aluno = db.get(
    Aluno,
    1
)


# UPDATE

aluno.nome_aluno = "Pedro Souza"

db.commit()


# DELETE

db.delete(aluno)

db.commit()


# ============================================================
# RESUMO DOS PRINCIPAIS COMANDOS ORM
# ============================================================


# CONSULTAR TODOS

db.scalars(
    select(Aluno)
).all()


# CONSULTAR COM FILTRO

db.scalars(
    select(Aluno)
    .where(
        Aluno.id > 5
    )
).all()


# BUSCAR POR ID

db.get(
    Aluno,
    1
)


# INSERIR

db.add(
    objeto
)

db.commit()


# ATUALIZAR

objeto.nome_aluno = "Novo Nome"

db.commit()


# EXCLUIR

db.delete(
    objeto
)

db.commit()


# CONFIRMAR TRANSAÇÃO

db.commit()


# DESFAZER TRANSAÇÃO

db.rollback()