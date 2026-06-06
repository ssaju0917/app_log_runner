"""change name length in users

Revision ID: e5024e8a2b06
Revises: c76f564eb1d1
Create Date: 2026-05-25 10:26:40.263524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5024e8a2b06'
down_revision: Union[str, Sequence[str], None] = 'c76f564eb1d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 生成されたファイルを手動で修正する例
def upgrade() -> None:
    op.alter_column('users', 'name',
        existing_type=sa.String(),
        type_=sa.String(100),
        nullable=False
    )

def downgrade() -> None:
    op.alter_column('users', 'name',
        existing_type=sa.String(100),
        type_=sa.String(),
        nullable=False
    )
