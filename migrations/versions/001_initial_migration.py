"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('master_password_hash', sa.String(length=200), nullable=False),
        sa.Column('pin_hash', sa.String(length=200), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('failed_attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('avatar', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create security_methods table
    op.create_table('security_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('required', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create security_settings table
    op.create_table('security_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=True, server_default='15'),
        sa.Column('max_login_attempts', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('lockout_duration_minutes', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('ip_restriction_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('allowed_ips', sa.Text(), nullable=True),
        sa.Column('device_alert_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('last_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create vault_categories table
    op.create_table('vault_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vault_items table
    op.create_table('vault_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('encrypted_value', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra', sa.Text(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_sensitive', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vault_fields table
    op.create_table('vault_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=True, server_default='text'),
        sa.Column('is_required', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_sensitive', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('default_value', sa.String(length=255), nullable=True),
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vault_files table
    op.create_table('vault_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('encrypted_data', sa.LargeBinary(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.String(length=255), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_archived', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create activity_logs table
    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create backup_logs table
    op.create_table('backup_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('backup_id', sa.String(length=100), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('items_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('files_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('restored_items', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='success'),
        sa.Column('encrypted', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('restored_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('backup_id')
    )

    # Create trusted_devices table
    op.create_table('trusted_devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(length=100), nullable=False),
        sa.Column('user_agent', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('is_trusted', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create login_attempts table
    op.create_table('login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('endpoint', sa.String(length=100), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('attempt_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create login_logs table
    op.create_table('login_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('login_time', sa.DateTime(), nullable=True),
        sa.Column('logout_time', sa.DateTime(), nullable=True),
        sa.Column('login_success', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('login_logs')
    op.drop_table('login_attempts')
    op.drop_table('trusted_devices')
    op.drop_table('backup_logs')
    op.drop_table('activity_logs')
    op.drop_table('notes')
    op.drop_table('vault_files')
    op.drop_table('vault_fields')
    op.drop_table('vault_items')
    op.drop_table('vault_categories')
    op.drop_table('security_settings')
    op.drop_table('security_methods')
    op.drop_table('users')