from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '476bfeec2203'
down_revision: Union[str, Sequence[str], None] = '780d93db0c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'assessment_class_ranges',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('test_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('min_score', sa.Integer(), nullable=False),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('assessment_class_ranges')