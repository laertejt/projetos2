from fastapi import APIRouter
from sqlalchemy import text
import pandas as pd
from app.database import engine
from app.schemas import EnderecoIn, EnderecoUpdateIn

# Prefixo no plural
router = APIRouter(prefix="/enderecos")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "você está na rota endereços"}

@router.get("/pegar-dados-endereco")
def pegar_dados_endereco():
  # Tabela corrigida para o plural tb_enderecos
  query = "SELECT * FROM tb_enderecos"
  df = pd.read_sql(query, engine)
  return df.to_dict(orient="records")

@router.post("/criar-endereco")
def criar_endereco(endereco: EnderecoIn):
  df = pd.DataFrame([endereco.model_dump()])
  # Tabela corrigida para o plural tb_enderecos
  df.to_sql("tb_enderecos", engine, if_exists="append", index=False)
  return {"mensagem": "Endereço cadastrado com sucesso!"}

# Falta de "@" corrigida
@router.put("/atualizar-endereco/{id}")
def atualizar_endereco(id: int, endereco: EnderecoUpdateIn):
  campos_sql = ", ".join([f"{chave} = :{chave}" for chave in endereco.model_dump(exclude_unset=True).keys()])
  # Tabela corrigida para o plural tb_enderecos
  query = f"""
      UPDATE tb_enderecos
      SET {campos_sql}
      WHERE id = :id
  """ 
  with engine.connect() as conn:
    conn.execute(
      text(query),
      {"id":id, **endereco.model_dump(exclude_unset=True)}
    )
    conn.commit()
  return {"mensagem": "Endereço atualizado com sucesso."}

@router.delete("/deletar-endereco/{id}")
def deletar_endereco(id: int):
  # Tabela corrigida para o plural tb_enderecos
  query = f"DELETE FROM tb_enderecos WHERE id = {id}"
  with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit() 
  return {"mensagem": "Endereço deletado com sucesso."}