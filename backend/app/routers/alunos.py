from fastapi import APIRouter
from sqlalchemy import text
import pandas as pd
from app.database import engine
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

