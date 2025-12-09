#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加医技业务价值计算步骤到计算流程ID 31
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量 - 从backend目录
load_dotenv('backend/.env')

# 数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = 'postgresql://root:root@47.108.227.254:50016/hospital_value'
print(f"连接数据库: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

# 医技业务价值计算SQL
sql_content = """-- ============================================================================
-- 医技业务价值计算
-- ============================================================================
-- 功能: 统计医技序列各末级维度的工作量和业务价值
--
-- 输入参数:
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 数据来源:
--   charge_details           - 收费明细表
--   dimension_item_mappings  - 维度项目映射表
--   departments              - 科室表
--   model_nodes              - 模型节点表
--
-- 算法说明:
--   1. 检查-量表检查: 统计量表检查类收费金额
--   2. 检查-眼科检查: 统计眼科检查类收费金额
--   3. 检查-CT检查: 统计CT检查类收费金额
--   4. 检查-超声检查: 统计超声检查类收费金额
--   5. 检查-内窥镜检查: 统计内窥镜检查类收费金额
--   6. 检查-X线检查: 统计X线检查类收费金额
--   7. 检查-其他检查: 统计其他检查类收费金额
--   8. 化验-临床免疫学检验: 统计临床免疫学检验类收费金额
--   9. 化验-临床血液学检验: 统计临床血液学检验类收费金额
--   10. 化验-临床化学检验: 统计临床化学检验类收费金额
--   11. 化验-临床体液检验: 统计临床体液检验类收费金额
--   12. 化验-分子病理学技术与诊断: 统计分子病理学技术与诊断类收费金额
--   13. 化验-其他化验: 统计其他化验类收费金额
--   14. 化验-临床微生物与寄生虫学检验: 统计临床微生物与寄生虫学检验类收费金额
--   15. 麻醉-全身麻醉: 统计全身麻醉类收费金额
--   16. 麻醉-部位麻醉: 统计部位麻醉类收费金额
--   17. 麻醉-麻醉中监测: 统计麻醉中监测类收费金额
--   18. 麻醉-其他麻醉: 统计其他麻醉类收费金额
-- ============================================================================

"""

def add_step():
    with engine.connect() as conn:
        # 检查步骤是否已存在
        check_sql = text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = 31 AND name = '医技业务价值计算'
        """)
        result = conn.execute(check_sql)
        existing = result.fetchone()
        
        if existing:
            print(f"步骤已存在，ID: {existing[0]}，正在更新...")
            step_id = existing[0]
            
            # 更新步骤
            update_sql = text("""
                UPDATE calculation_steps
                SET code_content = :code_content,
                    description = '统计医技序列各末级维度的工作量和业务价值',
                    updated_at = NOW()
                WHERE id = :step_id
            """)
            conn.execute(update_sql, {
                'code_content': sql_content + get_insert_statements(),
                'step_id': step_id
            })
            conn.commit()
            print(f"步骤更新成功！步骤ID: {step_id}")
        else:
            # 插入新步骤
            insert_sql = text("""
                INSERT INTO calculation_steps (
                    workflow_id, name, description, code_type, code_content,
                    sort_order, is_enabled, created_at, updated_at
                )
                VALUES (
                    31, '医技业务价值计算', 
                    '统计医技序列各末级维度的工作量和业务价值',
                    'sql', :code_content, 3.00, TRUE, NOW(), NOW()
                )
                RETURNING id
            """)
            result = conn.execute(insert_sql, {
                'code_content': sql_content + get_insert_statements()
            })
            step_id = result.fetchone()[0]
            conn.commit()
            print(f"步骤创建成功！步骤ID: {step_id}")

def get_insert_statements():
    """生成所有维度的INSERT语句"""
    # 医技序列的所有末级维度
    dimensions = [
        # 检查维度
        ('dim-tech-exam-scale', '量表检查'),
        ('dim-tech-exam-ophth', '眼科检查'),
        ('dim-tech-exam-ct', 'CT检查'),
        ('dim-tech-exam-us', '超声检查'),
        ('dim-tech-exam-endo', '内窥镜检查'),
        ('dim-tech-exam-xray', 'X线检查'),
        ('dim-tech-exam-other', '其他检查'),
        # 化验维度
        ('dim-tech-lab-immu', '临床免疫学检验'),
        ('dim-tech-lab-blood', '临床血液学检验'),
        ('dim-tech-lab-chem', '临床化学检验'),
        ('dim-tech-lab-fluid', '临床体液检验'),
        ('dim-tech-lab-molecular', '分子病理学技术与诊断'),
        ('dim-tech-lab-other', '其他化验'),
        ('dim-tech-lab-micro', '临床微生物与寄生虫学检验'),
        # 麻醉维度
        ('dim-tech-ana-general', '全身麻醉'),
        ('dim-tech-ana-regional', '部位麻醉'),
        ('dim-tech-ana-mon', '麻醉中监测'),
        ('dim-tech-ana-other', '其他麻醉'),
    ]
    
    statements = []
    for dim_code, dim_name in dimensions:
        stmt = f"""
-- {dim_name}
INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_type,
    node_name,
    node_code,
    parent_id,
    workload,
    weight,
    original_weight,
    value,
    created_at
)
SELECT
    '{{task_id}}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {{hospital_id}}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {{version_id}}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {{hospital_id}}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{{current_year_month}}'
  AND mn.code = '{dim_code}'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""
        statements.append(stmt)
    
    # 添加返回插入记录数的语句
    statements.append("""
-- 返回插入的记录数
SELECT COUNT(*) as inserted_count
FROM calculation_results
WHERE task_id = '{task_id}'
  AND node_type = 'dimension'
  AND node_code LIKE 'dim-tech%';
""")
    
    return '\n'.join(statements)

if __name__ == '__main__':
    add_step()
