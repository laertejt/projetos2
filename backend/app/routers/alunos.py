from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Aluno
from app.schemas import AlunoIn, AlunoOut, AlunoUpdateIn

router = APIRouter(prefix="/alunos")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "Hello, World!"}

@router.get("/pegar-dados-aluno", response_model=list[AlunoOut])
def pegar_dados_alunos(db: Session = Depends(get_db)):
  return db.scalars(select(Aluno).order_by(Aluno.id)).all()

@router.get("/pegar-dados-aluno-por-id/{id}", response_model=list[AlunoOut])
def pegar_dados_alunos_por_id(id: int, db: Session = Depends(get_db)):
  aluno = db.get(Aluno, id)
  return [aluno] if aluno is not None else []

@router.post("/criar-aluno")
def criar_aluno(aluno: AlunoIn, db: Session = Depends(get_db)):
  novo_aluno = Aluno(**aluno.model_dump())
  db.add(novo_aluno)
  db.commit()
  return {"mensagem": "Aluno cadastrado com sucesso!"}

@router.put("/atualizar-aluno/{id}")
def atualizar_aluno(id: int, aluno: AlunoUpdateIn, db: Session = Depends(get_db)):
  aluno_db = db.get(Aluno, id)
  if aluno_db is None:
    raise HTTPException(status_code=404, detail="Aluno não encontrado.")

  for campo, valor in aluno.model_dump(exclude_unset=True).items():
    setattr(aluno_db, campo, valor)

  db.commit()
  return {"mensagem": "Aluno atualizado com sucesso."}

@router.delete("/deletar-aluno/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
  aluno = db.get(Aluno, id)
  if aluno is None:
    raise HTTPException(status_code=404, detail="Aluno não encontrado.")

  db.delete(aluno)
  db.commit()
  return {"mensagem": "Aluno deletado com sucesso."}





