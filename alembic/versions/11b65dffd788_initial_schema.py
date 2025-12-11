"""initial schema

Revision ID: 11b65dffd788
Revises:
Create Date: 2025-12-05 21:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

revision = '11b65dffd788'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    userrole_enum = postgresql.ENUM('user', 'admin', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)

    emotiontype_enum = postgresql.ENUM(
        'happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'disgust',
        name='emotiontype'
    )
    emotiontype_enum.create(op.get_bind(), checkfirst=True)

    options_enum = postgresql.ENUM('neutral', 'very_low', 'low', 'medium', 'high', name='options')
    options_enum.create(op.get_bind(), checkfirst=True)

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(length=50), unique=True, nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('role', userrole_enum, nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Test categories
    op.create_table(
        'test_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True)
    )

    # Questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('test_categories.id', ondelete='CASCADE')),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('audio_bytes', sa.LargeBinary(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Test attempts
    op.create_table(
        'test_attempts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('test_categories.id')),
        sa.Column('test_score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('overall_emotion', emotiontype_enum, nullable=True),
        sa.Column('attempt_date', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Question results
    op.create_table(
        'question_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('attempt_id', sa.Integer(), sa.ForeignKey('test_attempts.id', ondelete='CASCADE')),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id', ondelete='CASCADE')),
        sa.Column('user_answer_audio', sa.LargeBinary(), nullable=True),
        sa.Column('user_answer_text', sa.Text(), nullable=False),
        sa.Column('recognized_emotion', emotiontype_enum, nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0')
    )

    # Survey options
    op.create_table(
        'survey_options',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('option_text', options_enum, nullable=False, server_default='neutral'),
        sa.Column('weightage', sa.Float(), nullable=False)
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('survey_options')
    op.drop_table('question_results')
    op.drop_table('test_attempts')
    op.drop_table('questions')
    op.drop_table('test_categories')
    op.drop_table('users')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS options')
    op.execute('DROP TYPE IF EXISTS emotiontype')
    op.execute('DROP TYPE IF EXISTS userrole')
