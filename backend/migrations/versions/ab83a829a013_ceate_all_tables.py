from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = 'ab83a829a013'  # leave whatever alembic generated here
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), default='doctor'),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )

    op.create_table('patients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hospital_reg_no', sa.String(), unique=True, nullable=True),  # hospital card number
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer()),
        sa.Column('gender', sa.String()),
        sa.Column('contact', sa.String()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )

    op.create_table('visits',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id')),
        sa.Column('date', sa.DateTime(), default=datetime.utcnow),
        sa.Column('notes', sa.Text()),
    )

    op.create_table('symptoms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visit_id', sa.Integer(), sa.ForeignKey('visits.id')),
        sa.Column('description', sa.Text()),
    )

    op.create_table('signs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visit_id', sa.Integer(), sa.ForeignKey('visits.id')),
        sa.Column('description', sa.Text()),
    )

    op.create_table('vision_tests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visit_id', sa.Integer(), sa.ForeignKey('visits.id')),
        sa.Column('eye', sa.String()),
        sa.Column('acuity', sa.String()),
        sa.Column('notes', sa.Text()),
    )

    op.create_table('pentacam_tests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('visit_id', sa.Integer(), sa.ForeignKey('visits.id')),
        sa.Column('date', sa.DateTime(), default=datetime.utcnow),
        sa.Column('eye', sa.String()),
    )

    op.create_table('pentacam_values',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pentacam_test_id', sa.Integer(), sa.ForeignKey('pentacam_tests.id')),
        sa.Column('key', sa.String()),
        sa.Column('value', sa.String()),
    )


def downgrade():
    op.drop_table('pentacam_values')
    op.drop_table('pentacam_tests')
    op.drop_table('vision_tests')
    op.drop_table('signs')
    op.drop_table('symptoms')
    op.drop_table('visits')
    op.drop_table('patients')
    op.drop_table('users')