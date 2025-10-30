"""rename_error_message_to_execution_info

Revision ID: 3900f968ffe3
Revises: 20251029_183000
Create Date: 2025-10-29 22:28:28.517424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3900f968ffe3'
down_revision = '20251029_183000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 重命名 calculation_step_logs 表的 error_message 字段为 execution_info
    op.alter_column(
        'calculation_step_logs',
        'error_message',
        new_column_name='execution_info',
        existing_type=sa.Text(),
        existing_comment='执行信息',
        comment='执行信息'
    )


def downgrade() -> None:
    # 回滚：将 execution_info 改回 error_message
    op.alter_column(
        'calculation_step_logs',
        'execution_info',
        new_column_name='error_message',
        existing_type=sa.Text(),
        existing_comment='错误信息',
        comment='错误信息'
    )
