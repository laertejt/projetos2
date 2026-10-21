import re
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal, Optional

class EnderecoIn(BaseModel):
    cep: str = Field(max_length=10)
    endereco: str = Field(max_length=255)
    bairro: str = Field(max_length=50)
    cidade: str = Field(min_length=1, max_length=100)
    estado: str = Field(min_length=2, max_length=50)
    regiao: str = Field(max_length=50)

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

class AlunoOut(AlunoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int

class AlunoComCepIn(BaseModel):
    matricula: str = Field(min_length=1, max_length=20)
    nome_aluno: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=100)
    cep: str

    @field_validator('matricula', 'nome_aluno', 'email', mode='before')
    @classmethod
    def remover_espacos(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator('email')
    @classmethod
    def validar_email(cls, valor: str) -> str:
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', valor):
            raise ValueError('Email inválido.')
        return valor.lower()

    @field_validator('cep')
    @classmethod
    def validar_cep(cls, valor: str) -> str:
        valor = valor.strip()
        if not re.fullmatch(r'[0-9]{5}-?[0-9]{3}', valor):
            raise ValueError('CEP deve conter 8 dígitos, com ou sem hífen.')
        return valor.replace('-', '')

class SituacaoAcademicaOut(BaseModel):
    aluno_id: int
    matricula: str
    nome_aluno: str
    total_notas: int
    media: float | None
    situacao: Literal['aprovado', 'reprovado', 'sem_notas']

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
