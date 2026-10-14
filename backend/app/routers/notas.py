from fastapi import APIRouter
from sqlalchemy import text
import pandas as pd
from app.database import engine
# Importação corrigida para o singular (NotaIn, NotaUpdateIn)
from app.schemas import NotaIn, NotaUpdateIn 

# Prefixo no plural
router = APIRouter(prefix="/notas")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "você está na rota notas"}

@router.get("/pegar-dados-nota")
def pegar_dados_nota():
  query = "SELECT * FROM tb_notas"
  df = pd.read_sql(query, engine)
  return df.to_dict(orient="records")

@router.post("/criar-nota")
def criar_nota(nota: NotaIn): # Variáveis no singular
  df = pd.DataFrame([nota.model_dump()])
  df.to_sql("tb_notas", engine, if_exists="append", index=False)
  return {"mensagem": "Nota cadastrada com sucesso!"}

# Falta de "@" corrigida
@router.put("/atualizar-nota/{id}")
def atualizar_nota(id: int, nota: NotaUpdateIn):
  campos_sql = ", ".join([f"{chave} = :{chave}" for chave in nota.model_dump(exclude_unset=True).keys()])
  query = f"""
      UPDATE tb_notas
      SET {campos_sql}
      WHERE id = :id
  """ 
  with engine.connect() as conn:
    conn.execute(
      text(query),
      {"id":id, **nota.model_dump(exclude_unset=True)}
    )
    conn.commit()
  return {"mensagem": "Nota atualizada com sucesso."}

@router.delete("/deletar-nota/{id}")
def deletar_nota(id: int):
  query = f"DELETE FROM tb_notas WHERE id = {id}"
  with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit() 
  return {"mensagem": "Nota deletada com sucesso."}