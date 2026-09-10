"""refac constraint total value

Revision ID: 359dbddcdffe
Revises: 75b2a92c6952
Create Date: 2026-09-09 20:22:55.300051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '359dbddcdffe'
down_revision: Union[str, Sequence[str], None] = '75b2a92c6952'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.drop_constraint('ck_contract_total_value_positive', type_='check')
        batch_op.create_check_constraint(
            'ck_contract_total_value_positive',
            'total_value >= 0',
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.drop_constraint('ck_contract_total_value_positive', type_='check')
        batch_op.create_check_constraint(
            'ck_contract_total_value_positive',
            'total_value > 0',
        )
