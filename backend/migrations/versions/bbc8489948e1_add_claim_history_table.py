"""add_claim_history_table

Revision ID: bbc8489948e1
Revises: 
Create Date: 2026-03-17 09:38:00.153531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbc8489948e1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create all tables."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)
    
    # Create queries table
    op.create_table(
        'queries',
        sa.Column('query_id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=False),
        sa.Column('verdict', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('score_real', sa.Float(), nullable=False),
        sa.Column('score_rumor', sa.Float(), nullable=False),
        sa.Column('score_fake', sa.Float(), nullable=False),
        sa.Column('propagation_risk', sa.String(), nullable=False),
        sa.Column('propagation_score', sa.Float(), nullable=False),
        sa.Column('evidence_score', sa.Float(), nullable=False),
        sa.Column('model_breakdown', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_signals', sa.JSON(), nullable=True),
        sa.Column('claims', sa.JSON(), nullable=True),
        sa.Column('evidence_sources', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ),
        sa.PrimaryKeyConstraint('query_id')
    )
    op.create_index(op.f('ix_queries_session_id'), 'queries', ['session_id'], unique=False)
    
    # Create claim_history table
    op.create_table(
        'claim_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('verdict', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('confidence_label', sa.String(), nullable=False),
        sa.Column('scores', sa.JSON(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('key_signals', sa.JSON(), nullable=True),
        sa.Column('highlighted_text', sa.JSON(), nullable=True),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema - drop all tables."""
    op.drop_table('claim_history')
    op.drop_table('queries')
    op.drop_table('sessions')
    op.drop_table('users')
