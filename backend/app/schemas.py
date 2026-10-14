from pydantic import BaseModel
from typing import Optional

class EnderecoIn(BaseModel):
    cep: str
    endereco: str
    bairro: str  
    cidade: str
    estado: str
    regiao: str

class EnderecoUpdateIn(BaseModel):
    cep: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    regiao: Optional[str] = None

class AlunoIn(BaseModel):
    matricula: str
    nome_aluno: str
    email: str
    endereco_id: int

class AlunoUpdateIn(BaseModel):
    matricula: Optional[str] = None
    nome_aluno: Optional[str] = None
    email: Optional[str] = None
    endereco_id: Optional[int] = None

class DisciplinaIn(BaseModel):
    nome_disciplina: str
    carga: int
    semestre: int

class DisciplinaUpdateIn(BaseModel):
    nome_disciplina: Optional[str] = None
    carga: Optional[int] = None
    semestre: Optional[int] = None

class NotaIn(BaseModel):
    aluno_id: int
    disciplina_id: int
    nota: float

class NotaUpdateIn(BaseModel):
    aluno_id: Optional[int] = None
    disciplina_id: Optional[int] = None
    nota: Optional[float] = None