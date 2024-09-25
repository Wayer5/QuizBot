"""Initial migration

Revision ID: 0d5b780bf7ec
Revises:
Create Date: 2024-09-24 19:43:12.156310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d5b780bf7ec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    """Создание таблиц и добавление колонок для первоначальной миграции."""

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    )
    op.create_table('quizzes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id']),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('quiz_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('total_questions', sa.Integer(), nullable=False),
    sa.Column('correct_answers_count', sa.Integer(), nullable=False),
    sa.Column('is_complete', sa.Boolean(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id']),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('variants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_right_choice', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('user_answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('answer_id', sa.Integer(), nullable=False),
    sa.Column('is_right', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['answer_id'], ['variants.id']),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
    sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:

    """Удаление таблиц при откате миграции."""

    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_answers')
    op.drop_table('variants')
    op.drop_table('quiz_results')
    op.drop_table('questions')
    op.drop_table('quizzes')
    op.drop_table('categories')
    # ### end Alembic commands ###
