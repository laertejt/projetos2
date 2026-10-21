import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import URLError

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from alembic.migration import MigrationContext
from alembic.operations import Operations

# A suíte usa apenas SQLite e respostas simuladas do ViaCEP.
with patch.dict(os.environ, {
    'user': 'test', 'senha': 'test', 'host': 'localhost', 'porta': '5432', 'banco': 'test',
    'MYSQL_USER': 'test', 'MYSQL_PASSWORD': 'test', 'MYSQL_HOST': 'localhost', 'MYSQL_DATABASE': 'test',
}):
    from app.database import Base
    from app.models import Aluno, Disciplina, Endereco, Nota
    from app.routers.alunos import router
    from app.schemas import AlunoComCepIn, AlunoIn, AlunoOut, AlunoUpdateIn, EnderecoIn
    from app.services import aluno_service, cep_service


ENDERECO = dict(cep='01001-000', endereco='Praça da Sé', bairro='Sé', cidade='São Paulo', estado='SP', regiao='Sudeste')
VIACEP = dict(cep='01001-000', logradouro='Praça da Sé', bairro='Sé', localidade='São Paulo', uf='SP', regiao='Sudeste')


class AlunoServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'autocommit': False})
        @event.listens_for(self.engine, 'connect')
        def foreign_keys(connection, _):
            # PRAGMA precisa ser executado fora da transação.
            connection.autocommit = True
            connection.execute('PRAGMA foreign_keys=ON')
            connection.autocommit = False
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)
        self.cep_mock = patch.object(cep_service, 'consultar_cep', return_value=EnderecoIn(**ENDERECO)).start()
        self.addCleanup(patch.stopall)

    def dados(self, **changes):
        return AlunoComCepIn(**dict(dict(matricula='001', nome_aluno='Ana', email='ana@example.com', cep='01001000'), **changes))

    def criar(self, **changes):
        return aluno_service.criar_com_cep(self.db, self.dados(**changes))

    def assert_status(self, status, callback):
        with self.assertRaises(HTTPException) as raised:
            callback()
        self.assertEqual(raised.exception.status_code, status)

    def test_cadastro_normalizacao_e_serializacao(self):
        aluno = self.criar(email=' ANA@EXAMPLE.COM ', cep='01001-000')
        self.assertEqual(AlunoOut.model_validate(aluno).email, 'ana@example.com')
        self.assertEqual(self.db.get(Endereco, aluno.endereco_id).cep, '01001-000')
        self.cep_mock.assert_called_once_with('01001000')
        with Session(self.engine) as other:
            self.assertEqual(other.scalar(select(func.count(Aluno.id))), 1)

    def test_reutiliza_endereco_com_e_sem_hifen(self):
        for cep in ('01001000', '01001-000'):
            with self.subTest(cep=cep):
                existente = self.db.scalar(select(Endereco))
                if existente is None:
                    self.db.add(Endereco(**dict(ENDERECO, cep=cep)))
                    self.db.commit()
                else:
                    existente.cep = cep
                    self.db.commit()
                aluno = self.criar(matricula=cep, email=f'{cep}@example.com')
                self.assertEqual(self.db.scalar(select(func.count(Endereco.id))), 1)
                self.assertEqual(aluno.endereco_id, self.db.scalar(select(Endereco.id)))

    def test_banco_impede_matricula_e_email_duplicados(self):
        self.criar()
        for dados in ({'email': 'outra@example.com'}, {'matricula': '002', 'email': 'ANA@example.com'}):
            with self.subTest(dados=dados), self.assertRaises(IntegrityError):
                self.criar(**dados)
            self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count(Aluno.id))), 1)

    def test_indice_impede_email_duplicado_fora_do_service(self):
        aluno = self.criar()
        self.db.add(Aluno(matricula='002', nome_aluno='Outra', email=' ANA@EXAMPLE.COM ', endereco_id=aluno.endereco_id))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_fechar_sessao_desfaz_cadastro_com_falha(self):
        with patch.object(self.db, 'commit', side_effect=IntegrityError('insert', {}, Exception('conflito'))):
            with self.assertRaises(IntegrityError):
                self.criar()
        # get_db() fecha a sessão ao final da requisição, inclusive em caso de erro.
        self.db.close()
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count(Endereco.id))), 0)
            self.assertEqual(db.scalar(select(func.count(Aluno.id))), 0)

    def test_falha_viacep_nao_grava(self):
        self.cep_mock.side_effect = HTTPException(504, 'timeout')
        self.assert_status(504, self.criar)
        self.assertEqual(self.db.scalar(select(func.count(Endereco.id))), 0)

    def test_crud_antigo_respeita_restricoes_do_banco(self):
        primeiro = self.criar()
        segundo = self.criar(matricula='002', email='outra@example.com')
        with self.assertRaises(IntegrityError):
            aluno_service.criar_aluno(self.db, AlunoIn(
                matricula='003', nome_aluno='Teste', email='ANA@example.com', endereco_id=primeiro.endereco_id))
        self.db.rollback()
        with self.assertRaises(IntegrityError):
            aluno_service.atualizar_aluno(self.db, segundo.id, AlunoUpdateIn(email=primeiro.email))
        self.db.rollback()
        with self.assertRaises(IntegrityError):
            aluno_service.atualizar_aluno(self.db, segundo.id, AlunoUpdateIn(matricula=primeiro.matricula))
        self.db.rollback()
        aluno_service.atualizar_aluno(self.db, primeiro.id, AlunoUpdateIn(nome_aluno='Ana Atualizada'))
        self.assertEqual(primeiro.nome_aluno, 'Ana Atualizada')

    def test_sem_notas_e_aluno_inexistente(self):
        aluno = self.criar()
        resultado = aluno_service.situacao_academica(self.db, aluno.id)
        self.assertEqual((resultado.media, resultado.situacao, resultado.total_notas), (None, 'sem_notas', 0))
        self.assert_status(404, lambda: aluno_service.situacao_academica(self.db, 999))

    def test_media_aprovacao_reprovacao_e_arredondamento(self):
        aluno = self.criar()
        outro = self.criar(matricula='002', email='outra@example.com')
        disciplina = Disciplina(nome_disciplina='Matemática', carga=60, semestre=1)
        self.db.add(disciplina)
        self.db.flush()
        self.db.add(Nota(aluno_id=outro.id, disciplina_id=disciplina.id, nota=0))
        for notas, esperado in (
            (['6', '8'], (7.0, 'aprovado')),
            (['0', '6'], (3.0, 'reprovado')),
            (['6.99', '7'], (7.0, 'reprovado')),
        ):
            with self.subTest(notas=notas):
                for nota in self.db.scalars(select(Nota).where(Nota.aluno_id == aluno.id)):
                    self.db.delete(nota)
                self.db.add_all([Nota(aluno_id=aluno.id, disciplina_id=disciplina.id, nota=Decimal(n)) for n in notas])
                self.db.commit()
                resultado = aluno_service.situacao_academica(self.db, aluno.id)
                self.assertEqual((resultado.media, resultado.situacao), esperado)
                self.assertEqual(resultado.total_notas, 2)


class CepServiceTests(unittest.TestCase):
    def resposta(self, dados):
        return patch.object(cep_service, 'urlopen', return_value=io.BytesIO(json.dumps(dados).encode()))

    def test_mapeamento(self):
        with self.resposta(VIACEP):
            self.assertEqual(cep_service.consultar_cep('01001-000').model_dump(), ENDERECO)

    def test_ceps_invalidos(self):
        with patch.object(cep_service, 'urlopen') as chamada:
            for cep in ('123', '01001A00', '１２３４５６７８', '010010000'):
                with self.subTest(cep=cep), self.assertRaises(HTTPException) as raised:
                    cep_service.consultar_cep(cep)
                self.assertEqual(raised.exception.status_code, 422)
            chamada.assert_not_called()

    def test_erros_do_provedor(self):
        for dados, status in [({'erro': True}, 404), ({'erro': 'true'}, 404), ([], 502), ({}, 502), (dict(VIACEP, cep='99999999'), 502)]:
            with self.subTest(dados=dados), self.resposta(dados), self.assertRaises(HTTPException) as raised:
                cep_service.consultar_cep('01001000')
            self.assertEqual(raised.exception.status_code, status)

    def test_timeout_e_rede(self):
        for erro, status in [(TimeoutError(), 502), (URLError(TimeoutError()), 502), (URLError('offline'), 502), (ConnectionResetError(), 502)]:
            with self.subTest(erro=erro), patch.object(cep_service, 'urlopen', side_effect=erro), self.assertRaises(HTTPException) as raised:
                cep_service.consultar_cep('01001000')
            self.assertEqual(raised.exception.status_code, status)

    def test_json_invalido(self):
        with patch.object(cep_service, 'urlopen', return_value=io.BytesIO(b'not json')), self.assertRaises(HTTPException) as raised:
            cep_service.consultar_cep('01001000')
        self.assertEqual(raised.exception.status_code, 502)

    def test_schema_rejeita_dados_invalidos(self):
        for changes in ({'cep': '123'}, {'email': 'invalido'}, {'matricula': ' '}, {'nome_aluno': ' '}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                AlunoComCepIn(**dict(dict(matricula='001', nome_aluno='Ana', email='ana@example.com', cep='01001000'), **changes))


class ContratoMigrationTests(unittest.TestCase):
    def test_contratos_openapi(self):
        app = FastAPI()
        app.include_router(router)
        paths = app.openapi()['paths']
        self.assertIn('201', paths['/alunos/criar-com-cep']['post']['responses'])
        self.assertIn('200', paths['/alunos/{id}/situacao-academica']['get']['responses'])

    def test_migration_compila_para_postgresql(self):
        arquivo = Path(__file__).resolve().parents[1] / 'alembic/versions/a7c29e314b80_email_unico_aluno.py'
        spec = importlib.util.spec_from_file_location('migration_email', arquivo)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        output = io.StringIO()
        context = MigrationContext.configure(dialect_name='postgresql', opts={'as_sql': True, 'output_buffer': output})
        with Operations.context(context):
            migration.upgrade()
            migration.downgrade()
        self.assertIn('CREATE UNIQUE INDEX uq_tb_alunos_email ON tb_alunos (lower(trim(email)))', output.getvalue())
        self.assertIn('DROP INDEX uq_tb_alunos_email', output.getvalue())


if __name__ == '__main__':
    unittest.main()
