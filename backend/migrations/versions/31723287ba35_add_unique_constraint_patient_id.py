"""add_unique_constraint_patient_id

Revision ID: 31723287ba35
Revises: ab83a829a013
Create Date: 2026-06-08 17:32:27.204227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31723287ba35'
down_revision: Union[str, Sequence[str], None] = 'ab83a829a013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_unique_constraint(
        "uq_patients_hospital_reg_no",
        "patients",
        ["hospital_reg_no"]
    )


def downgrade() -> None:
   op.drop_constraint(
        "uq_patients_hospital_reg_no",
        "patients")
   