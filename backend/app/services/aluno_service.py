from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Aluno, Endereco, Nota
from app.schemas import AlunoComCepIn, AlunoIn, AlunoUpdateIn, SituacaoAcademicaOut
from app.services import cep_service


def listar_alunos(db: Session):
    return db.scalars(select(Aluno).order_by(Aluno.id)).all()


def listar_alunos_por_id(db: Session, aluno_id: int):
    aluno = db.get(Aluno, aluno_id)
    return [aluno] if aluno is not None else []


def buscar_aluno(db: Session, aluno_id: int) -> Aluno:
    aluno = db.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(status_code=404, detail='Aluno não encontrado.')
    return aluno


def criar_aluno(db: Session, dados: AlunoIn) -> Aluno:
    email = dados.email.strip().lower()
    if db.get(Endereco, dados.endereco_id) is None:
        raise HTTPException(status_code=404, detail='Endereço não encontrado.')
    aluno = Aluno(
        matricula=dados.matricula,
        nome_aluno=dados.nome_aluno,
        email=email,
        endereco_id=dados.endereco_id,
    )
    db.add(aluno)
    db.commit()
    return aluno


def criar_com_cep(db: Session, dados: AlunoComCepIn) -> Aluno:
    # 1. Consulta o endereço no ViaCEP.
    endereco_dados = cep_service.consultar_cep(dados.cep)
    # 2. Procura o CEP no banco, com ou sem hífen.
    consulta = select(Endereco).where(
        Endereco.cep.in_([dados.cep, endereco_dados.cep])
    )
    endereco = db.scalar(consulta)
    # 3. Cadastra o endereço somente se ele ainda não existe.
    if endereco is None:
        endereco = Endereco(
            cep=endereco_dados.cep,
            endereco=endereco_dados.endereco,
            bairro=endereco_dados.bairro,
            cidade=endereco_dados.cidade,
            estado=endereco_dados.estado,
            regiao=endereco_dados.regiao,
        )
        db.add(endereco)
        db.flush()  # Gera o ID do endereço, sem confirmar a transação.
    # 4. Cria o aluno usando o ID do endereço.
    aluno = Aluno(
        matricula=dados.matricula,
        nome_aluno=dados.nome_aluno,
        email=dados.email,
        endereco_id=endereco.id,
    )
    db.add(aluno)
    # 5. Salva endereço e aluno juntos.
    db.commit()
    return aluno


def atualizar_aluno(db: Session, aluno_id: int, dados: AlunoUpdateIn):
    aluno = buscar_aluno(db, aluno_id)
    campos = dados.model_dump(exclude_unset=True)
    if any(valor is None for valor in campos.values()):
        raise HTTPException(status_code=422, detail='Os campos do aluno não podem ser nulos.')
    if 'email' in campos:
        campos['email'] = campos['email'].strip().lower()
    if 'endereco_id' in campos and db.get(Endereco, campos['endereco_id']) is None:
        raise HTTPException(status_code=404, detail='Endereço não encontrado.')
    for campo, valor in campos.items():
        setattr(aluno, campo, valor)
    db.commit()


def deletar_aluno(db: Session, aluno_id: int):
    aluno = buscar_aluno(db, aluno_id)
    db.delete(aluno)
    db.commit()


def situacao_academica(db: Session, aluno_id: int) -> SituacaoAcademicaOut:
    aluno = buscar_aluno(db, aluno_id)
    notas = db.scalars(select(Nota.nota).where(Nota.aluno_id == aluno_id)).all()

    if len(notas) == 0:
        media = None
        situacao = 'sem_notas'
    else:
        media = sum(notas) / len(notas)

        if media >= 7:
            situacao = 'aprovado'
        else:
            situacao = 'reprovado'

        # Arredonda apenas o valor exibido na resposta.
        media = float(media.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    return SituacaoAcademicaOut(
        aluno_id=aluno.id,
        matricula=aluno.matricula,
        nome_aluno=aluno.nome_aluno,
        total_notas=len(notas),
        media=media,
        situacao=situacao,
    )
