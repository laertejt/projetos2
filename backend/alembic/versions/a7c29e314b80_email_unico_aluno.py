"""Impede emails duplicados, ignorando maiúsculas e espaços nas extremidades.

Revision ID: a7c29e314b80
Revises: d457a4c9930e
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7c29e314b80'
down_revision = 'd457a4c9930e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Se já houver duplicatas, o PostgreSQL rejeita a criação do índice.
    # Os registros devem ser corrigidos explicitamente, sem apagar dados aqui.
    op.create_index(
        'uq_tb_alunos_email', 'tb_alunos',
        [sa.text('lower(trim(email))')], unique=True,
    )


def downgrade() -> None:
    op.drop_index('uq_tb_alunos_email', table_name='tb_alunos')
