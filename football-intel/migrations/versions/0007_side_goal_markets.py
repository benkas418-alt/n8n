"""goal markets of side models (D107)

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-28 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNS = ("p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "exp_home_goals", "exp_away_goals")


def upgrade() -> None:
    for c in COLUMNS:
        op.add_column("side_predictions", sa.Column(c, sa.Float(), nullable=True))


def downgrade() -> None:
    for c in COLUMNS:
        op.drop_column("side_predictions", c)
