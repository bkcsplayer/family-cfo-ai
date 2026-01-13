"""Add v3.0 tables: categories, assets_v3, liabilities, documents

Revision ID: c7fc163ae2f7
Revises: 73aa1d282ca3
Create Date: 2026-01-01 21:48:36.790423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7fc163ae2f7'
down_revision: Union[str, None] = '73aa1d282ca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create CategoryType enum
    category_type_enum = postgresql.ENUM('income', 'expense', 'asset', 'liability', name='categorytype')
    category_type_enum.create(op.get_bind())

    # Create RefreshSource enum
    refresh_source_enum = postgresql.ENUM('manual', 'stock_api', 'crypto_api', 'real_estate_api', name='refreshsource')
    refresh_source_enum.create(op.get_bind())

    # Create PaymentFrequency enum
    payment_frequency_enum = postgresql.ENUM('weekly', 'biweekly', 'monthly', 'quarterly', 'semi_annually', 'annually', name='paymentfrequency')
    payment_frequency_enum.create(op.get_bind())

    # Create ParsingStatus enum
    parsing_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='parsingstatus')
    parsing_status_enum.create(op.get_bind())

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', category_type_enum, nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_type'), 'categories', ['type'], unique=False)

    # Create assets_v3 table
    op.create_table('assets_v3',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_value', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('appreciation_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('refresh_source', refresh_source_enum, nullable=False, server_default='manual'),
        sa.Column('last_refreshed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_v3_category_id'), 'assets_v3', ['category_id'], unique=False)
    op.create_index(op.f('ix_assets_v3_id'), 'assets_v3', ['id'], unique=False)
    op.create_index(op.f('ix_assets_v3_user_id'), 'assets_v3', ['user_id'], unique=False)

    # Create liabilities table
    op.create_table('liabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('principal_balance', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('payment_frequency', payment_frequency_enum, nullable=False, server_default='monthly'),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('next_payment_date', sa.Date(), nullable=True),
        sa.Column('origination_date', sa.Date(), nullable=True),
        sa.Column('maturity_date', sa.Date(), nullable=True),
        sa.Column('lender', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_liabilities_category_id'), 'liabilities', ['category_id'], unique=False)
    op.create_index(op.f('ix_liabilities_id'), 'liabilities', ['id'], unique=False)
    op.create_index(op.f('ix_liabilities_next_payment_date'), 'liabilities', ['next_payment_date'], unique=False)
    op.create_index(op.f('ix_liabilities_user_id'), 'liabilities', ['user_id'], unique=False)

    # Create documents table
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parsing_status', parsing_status_enum, nullable=False, server_default='pending'),
        sa.Column('ai_confidence', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('linked_entity', sa.String(length=50), nullable=True),
        sa.Column('linked_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    op.drop_index(op.f('ix_liabilities_user_id'), table_name='liabilities')
    op.drop_index(op.f('ix_liabilities_next_payment_date'), table_name='liabilities')
    op.drop_index(op.f('ix_liabilities_id'), table_name='liabilities')
    op.drop_index(op.f('ix_liabilities_category_id'), table_name='liabilities')
    op.drop_table('liabilities')

    op.drop_index(op.f('ix_assets_v3_user_id'), table_name='assets_v3')
    op.drop_index(op.f('ix_assets_v3_id'), table_name='assets_v3')
    op.drop_index(op.f('ix_assets_v3_category_id'), table_name='assets_v3')
    op.drop_table('assets_v3')

    op.drop_index(op.f('ix_categories_type'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')

    # Drop enums
    postgresql.ENUM(name='parsingstatus').drop(op.get_bind())
    postgresql.ENUM(name='paymentfrequency').drop(op.get_bind())
    postgresql.ENUM(name='refreshsource').drop(op.get_bind())
    postgresql.ENUM(name='categorytype').drop(op.get_bind())
