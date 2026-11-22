"""Unificar migraciones de sensores y busqueda de raices

Revision ID: 57a155a90030
Revises: b5f0e635d8c1, d847da31a189
Create Date: 2026-11-22 00:54:01.811206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57a155a90030'
down_revision = ('b5f0e635d8c1', 'd847da31a189')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
