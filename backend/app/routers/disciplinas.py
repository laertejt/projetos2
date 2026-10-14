from fastapi import APIRouter
from sqlalchemy import text
import pandas as pd
from app.database import engine
from app.schemas import DisciplinaIn, DisciplinaUpdateIn

# Prefixo no plural
router = APIRouter(prefix="/disciplinas")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "você está na rota disciplinas"}

@router.get("/pegar-dados-disciplina")
def pegar_dados_disciplina():
  query = "SELECT * FROM tb_disciplinas"
  df = pd.read_sql(query, engine)
  return df.to_dict(orient="records")

@router.post("/criar-disciplina")
def criar_disciplina(disciplina: DisciplinaIn): # Variáveis no singular
  df = pd.DataFrame([disciplina.model_dump()])
  df.to_sql("tb_disciplinas", engine, if_exists="append", index=False)
  return {"mensagem": "Disciplina cadastrada com sucesso!"}

# Falta de "@" corrigida
@router.put("/atualizar-disciplina/{id}")
def atualizar_disciplina(id: int, disciplina: DisciplinaUpdateIn):
  campos_sql = ", ".join([f"{chave} = :{chave}" for chave in disciplina.model_dump(exclude_unset=True).keys()])
  query = f"""
      UPDATE tb_disciplinas
      SET {campos_sql}
      WHERE id = :id
  """ 
  with engine.connect() as conn:
    conn.execute(
      text(query),
      {"id":id, **disciplina.model_dump(exclude_unset=True)}
    )
    conn.commit()
  return {"mensagem": "Disciplina atualizada com sucesso."}

@router.delete("/deletar-disciplina/{id}")
def deletar_disciplina(id: int):
  query = f"DELETE FROM tb_disciplinas WHERE id = {id}"
  with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit() 
  return {"mensagem": "Disciplina deletada com sucesso."}