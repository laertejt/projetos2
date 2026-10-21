from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AlunoComCepIn, AlunoIn, AlunoOut, AlunoUpdateIn, SituacaoAcademicaOut
from app.services import aluno_service

router = APIRouter(prefix="/alunos")

@router.get("/pegar-mensagem")
def primeira_api():
  return {"message": "Hello, World!"}

@router.get("/pegar-dados-aluno", response_model=list[AlunoOut])
def pegar_dados_alunos(db: Session = Depends(get_db)):
  return aluno_service.listar_alunos(db)

@router.get("/pegar-dados-aluno-por-id/{id}", response_model=list[AlunoOut])
def pegar_dados_alunos_por_id(id: int, db: Session = Depends(get_db)):
  # A rota antiga mantém uma lista vazia para IDs inexistentes.
  return aluno_service.listar_alunos_por_id(db, id)

@router.post("/criar-com-cep", response_model=AlunoOut, status_code=201)
def criar_com_cep(aluno: AlunoComCepIn, db: Session = Depends(get_db)):
  return aluno_service.criar_com_cep(db, aluno)

@router.get("/{id}/situacao-academica", response_model=SituacaoAcademicaOut)
def situacao_academica(id: int, db: Session = Depends(get_db)):
  return aluno_service.situacao_academica(db, id)

@router.post("/criar-aluno")
def criar_aluno(aluno: AlunoIn, db: Session = Depends(get_db)):
  aluno_service.criar_aluno(db, aluno)
  return {"mensagem": "Aluno cadastrado com sucesso!"}

@router.put("/atualizar-aluno/{id}")
def atualizar_aluno(id: int, aluno: AlunoUpdateIn, db: Session = Depends(get_db)):
  aluno_service.atualizar_aluno(db, id, aluno)
  return {"mensagem": "Aluno atualizado com sucesso."}

@router.delete("/deletar-aluno/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
  aluno_service.deletar_aluno(db, id)
  return {"mensagem": "Aluno deletado com sucesso."}





