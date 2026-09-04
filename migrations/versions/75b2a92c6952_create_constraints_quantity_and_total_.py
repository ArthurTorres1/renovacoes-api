"""create constraints quantity and total_value

Revision ID: 75b2a92c6952
Revises: bed9c878898a
Create Date: 2026-09-04 10:22:31.478518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b2a92c6952'
down_revision: Union[str, Sequence[str], None] = 'bed9c878898a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_contracts_vendor_contract_id', ['vendor_contract_id'])
        batch_op.create_check_constraint('ck_contract_quantity_positive', 'quantity > 0')
        batch_op.create_check_constraint('ck_contract_total_value_positive', 'total_value > 0')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.drop_constraint('ck_contract_total_value_positive', type_='check')
        batch_op.drop_constraint('ck_contract_quantity_positive', type_='check')
        batch_op.drop_constraint('uq_contracts_vendor_contract_id', type_='unique')
