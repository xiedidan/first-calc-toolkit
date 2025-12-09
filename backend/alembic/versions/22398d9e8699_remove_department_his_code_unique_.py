"""remove_department_his_code_unique_constraint

Revision ID: 22398d9e8699
Revises: 20251203_merge
Create Date: 2025-12-04 17:05:42.986008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22398d9e8699'
down_revision = '20251203_merge'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 删除 departments 表的 (hospital_id, his_code) 唯一约束
    # 允许同一医疗机构内存在相同的 HIS 科室代码
    op.drop_constraint('uq_departments_hospital_his_code', 'departments', type_='unique')


def downgrade() -> None:
    # 恢复唯一约束
    op.create_unique_constraint('uq_departments_hospital_his_code', 'departments', ['hospital_id', 'his_code'])
