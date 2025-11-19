# 测试数据插入 - 计算流程步骤版本

将测试数据插入拆分为多个计算步骤，可以放到计算流程中执行。

---

## 步骤 1：插入医生序列数据

**步骤名称：** 01-插入医生序列测试数据  
**代码类型：** SQL  
**排序：** 1.00

```sql
-- 插入医生序列及其维度数据
DO $$
DECLARE
    v_task_id VARCHAR(100) := '{task_id}';
    v_dept_id INTEGER;
    v_dept_code VARCHAR(50);
    v_dept_name VARCHAR(100);
    v_random_factor NUMERIC;
    v_doctor_seq_id INTEGER := 1;
    v_outpatient_id INTEGER := 11;
    v_inpatient_id INTEGER := 12;
    v_surgery_id INTEGER := 13;
BEGIN
    -- 获取科室信息
    FOR v_dept_id, v_dept_code, v_dept_name IN 
        SELECT id, his_code, his_name 
        FROM departments 
        WHERE ('{department_code}' = '' OR his_code = '{department_code}')
          AND is_active = TRUE 
        ORDER BY sort_order
        LIMIT CASE WHEN '{department_code}' = '' THEN 20 ELSE 1 END
    LOOP
        v_random_factor := 0.5 + random();
        
        -- 医生序列汇总
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, value, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_doctor_seq_id, '医生序列', 'DOCTOR_SEQ', 'sequence',
            NULL, (50000 + random() * 100000) * v_random_factor, NOW()
        );
        
        -- 门诊诊察
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_outpatient_id, '门诊诊察', 'OUTPATIENT', 'dimension',
            v_doctor_seq_id, 
            (500 + random() * 1000) * v_random_factor,
            30 + random() * 20,
            (20000 + random() * 40000) * v_random_factor,
            25 + random() * 15,
            NOW()
        );
        
        -- 住院诊察
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_inpatient_id, '住院诊察', 'INPATIENT', 'dimension',
            v_doctor_seq_id,
            (200 + random() * 400) * v_random_factor,
            80 + random() * 40,
            (15000 + random() * 35000) * v_random_factor,
            20 + random() * 15,
            NOW()
        );
        
        -- 手术
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_surgery_id, '手术', 'SURGERY', 'dimension',
            v_doctor_seq_id,
            (50 + random() * 150) * v_random_factor,
            200 + random() * 300,
            (15000 + random() * 40000) * v_random_factor,
            15 + random() * 20,
            NOW()
        );
        
    END LOOP;
END $$;
```

---

## 步骤 2：插入护理序列数据

**步骤名称：** 02-插入护理序列测试数据  
**代码类型：** SQL  
**排序：** 2.00

```sql
-- 插入护理序列及其维度数据
DO $$
DECLARE
    v_task_id VARCHAR(100) := '{task_id}';
    v_dept_id INTEGER;
    v_dept_code VARCHAR(50);
    v_dept_name VARCHAR(100);
    v_random_factor NUMERIC;
    v_nurse_seq_id INTEGER := 2;
    v_bed_nursing_id INTEGER := 21;
    v_special_nursing_id INTEGER := 22;
BEGIN
    FOR v_dept_id, v_dept_code, v_dept_name IN 
        SELECT id, his_code, his_name 
        FROM departments 
        WHERE ('{department_code}' = '' OR his_code = '{department_code}')
          AND is_active = TRUE 
        ORDER BY sort_order
        LIMIT CASE WHEN '{department_code}' = '' THEN 20 ELSE 1 END
    LOOP
        v_random_factor := 0.5 + random();
        
        -- 护理序列汇总
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, value, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_nurse_seq_id, '护理序列', 'NURSE_SEQ', 'sequence',
            NULL, (30000 + random() * 60000) * v_random_factor, NOW()
        );
        
        -- 床日护理
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_bed_nursing_id, '床日护理', 'BED_NURSING', 'dimension',
            v_nurse_seq_id,
            (800 + random() * 1200) * v_random_factor,
            25 + random() * 15,
            (20000 + random() * 40000) * v_random_factor,
            40 + random() * 20,
            NOW()
        );
        
        -- 专科护理
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_special_nursing_id, '专科护理', 'SPECIAL_NURSING', 'dimension',
            v_nurse_seq_id,
            (100 + random() * 300) * v_random_factor,
            50 + random() * 50,
            (10000 + random() * 30000) * v_random_factor,
            20 + random() * 20,
            NOW()
        );
        
    END LOOP;
END $$;
```

---

## 步骤 3：插入医技序列数据

**步骤名称：** 03-插入医技序列测试数据  
**代码类型：** SQL  
**排序：** 3.00

```sql
-- 插入医技序列及其维度数据
DO $$
DECLARE
    v_task_id VARCHAR(100) := '{task_id}';
    v_dept_id INTEGER;
    v_dept_code VARCHAR(50);
    v_dept_name VARCHAR(100);
    v_random_factor NUMERIC;
    v_tech_seq_id INTEGER := 3;
    v_radiology_id INTEGER := 31;
    v_lab_id INTEGER := 32;
BEGIN
    FOR v_dept_id, v_dept_code, v_dept_name IN 
        SELECT id, his_code, his_name 
        FROM departments 
        WHERE ('{department_code}' = '' OR his_code = '{department_code}')
          AND is_active = TRUE 
        ORDER BY sort_order
        LIMIT CASE WHEN '{department_code}' = '' THEN 20 ELSE 1 END
    LOOP
        v_random_factor := 0.5 + random();
        
        -- 医技序列汇总
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, value, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_tech_seq_id, '医技序列', 'TECH_SEQ', 'sequence',
            NULL, (20000 + random() * 40000) * v_random_factor, NOW()
        );
        
        -- 放射检查
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_radiology_id, '放射检查', 'RADIOLOGY', 'dimension',
            v_tech_seq_id,
            (200 + random() * 400) * v_random_factor,
            40 + random() * 30,
            (10000 + random() * 25000) * v_random_factor,
            40 + random() * 20,
            NOW()
        );
        
        -- 检验
        INSERT INTO calculation_results (
            task_id, department_id, node_id, node_name, node_code, node_type,
            parent_id, workload, weight, value, ratio, created_at
        ) VALUES (
            v_task_id, v_dept_id, v_lab_id, '检验', 'LAB', 'dimension',
            v_tech_seq_id,
            (300 + random() * 500) * v_random_factor,
            20 + random() * 20,
            (8000 + random() * 20000) * v_random_factor,
            30 + random() * 20,
            NOW()
        );
        
    END LOOP;
END $$;
```

---

## 步骤 4：生成汇总数据

**步骤名称：** 04-生成汇总数据  
**代码类型：** SQL  
**排序：** 4.00

```sql
-- 根据结果数据生成汇总
DO $$
DECLARE
    v_task_id VARCHAR(100) := '{task_id}';
    v_dept_id INTEGER;
    v_doctor_value NUMERIC;
    v_nurse_value NUMERIC;
    v_tech_value NUMERIC;
    v_total_value NUMERIC;
BEGIN
    -- 遍历所有有结果的科室
    FOR v_dept_id IN 
        SELECT DISTINCT department_id 
        FROM calculation_results 
        WHERE task_id = v_task_id
    LOOP
        -- 计算各序列的价值
        SELECT 
            COALESCE(SUM(CASE WHEN node_name LIKE '%医生%' THEN value ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN node_name LIKE '%护理%' THEN value ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN node_name LIKE '%医技%' THEN value ELSE 0 END), 0)
        INTO v_doctor_value, v_nurse_value, v_tech_value
        FROM calculation_results
        WHERE task_id = v_task_id
          AND department_id = v_dept_id
          AND node_type = 'sequence';
        
        v_total_value := v_doctor_value + v_nurse_value + v_tech_value;
        
        -- 插入或更新汇总记录
        INSERT INTO calculation_summaries (
            task_id, department_id,
            doctor_value, doctor_ratio,
            nurse_value, nurse_ratio,
            tech_value, tech_ratio,
            total_value, created_at
        ) VALUES (
            v_task_id, v_dept_id,
            v_doctor_value, 
            CASE WHEN v_total_value > 0 THEN (v_doctor_value / v_total_value * 100) ELSE 0 END,
            v_nurse_value,
            CASE WHEN v_total_value > 0 THEN (v_nurse_value / v_total_value * 100) ELSE 0 END,
            v_tech_value,
            CASE WHEN v_total_value > 0 THEN (v_tech_value / v_total_value * 100) ELSE 0 END,
            v_total_value,
            NOW()
        )
        ON CONFLICT (task_id, department_id) 
        DO UPDATE SET
            doctor_value = EXCLUDED.doctor_value,
            doctor_ratio = EXCLUDED.doctor_ratio,
            nurse_value = EXCLUDED.nurse_value,
            nurse_ratio = EXCLUDED.nurse_ratio,
            tech_value = EXCLUDED.tech_value,
            tech_ratio = EXCLUDED.tech_ratio,
            total_value = EXCLUDED.total_value;
        
    END LOOP;
END $$;
```

---

## 步骤 5：验证数据

**步骤名称：** 05-验证测试数据  
**代码类型：** SQL  
**排序：** 5.00

```sql
-- 返回插入的数据统计
SELECT 
    '{task_id}' as task_id,
    '{period}' as period,
    '{department_code}' as department_filter,
    CASE WHEN '{department_code}' = '' THEN '批量模式' ELSE '单科室模式' END as execution_mode,
    COUNT(DISTINCT department_id) as department_count,
    COUNT(*) FILTER (WHERE node_type = 'sequence') as sequence_count,
    COUNT(*) FILTER (WHERE node_type = 'dimension') as dimension_count,
    COUNT(*) as total_result_records,
    ROUND(SUM(value), 2) as total_value,
    (SELECT COUNT(*) FROM calculation_summaries WHERE task_id = '{task_id}') as summary_records
FROM calculation_results
WHERE task_id = '{task_id}';
```

---

## 使用说明

### 1. 创建计算流程

1. 进入"计算流程管理"
2. 创建新流程：
   - 流程名称：`测试数据生成流程`
   - 流程描述：`自动生成测试结果数据用于报表功能测试`
   - 关联模型版本：任意版本

### 2. 添加计算步骤

按照上面的顺序，创建 5 个计算步骤：
- 步骤 1：插入医生序列数据
- 步骤 2：插入护理序列数据
- 步骤 3：插入医技序列数据
- 步骤 4：生成汇总数据
- 步骤 5：验证数据

每个步骤：
- 代码类型：SQL
- 数据源：选择你的 PostgreSQL 数据源
- 代码内容：复制对应的 SQL
- 排序序号：1.00, 2.00, 3.00, 4.00, 5.00
- 是否启用：全部启用

### 3. 执行计算任务

**批量模式（推荐）：**
- 不选择科室
- 会为所有启用的科室（最多20个）生成测试数据

**单科室模式：**
- 选择1个科室
- 只为该科室生成测试数据

### 4. 查看结果

任务完成后：
1. 进入"结果查询"页面
2. 选择对应的计算周期
3. 查看生成的测试数据

---

## 优势

✅ **自动化**：无需手动填写任务ID  
✅ **灵活**：支持单科室和批量两种模式  
✅ **可重复**：可以多次执行生成不同的测试数据  
✅ **可追踪**：每次执行都有完整的步骤日志  
✅ **易维护**：分步骤便于调试和修改

---

## 注意事项

1. **节点ID**：脚本使用固定的节点ID（1, 2, 3, 11, 12...），如果你的数据库中有实际的模型节点，建议修改为实际的节点ID

2. **科室数量**：批量模式限制为20个科室，可以修改 `LIMIT 20` 调整数量

3. **数据清理**：如果需要重新生成，先删除旧数据：
   ```sql
   DELETE FROM calculation_results WHERE task_id = 'YOUR_TASK_ID';
   DELETE FROM calculation_summaries WHERE task_id = 'YOUR_TASK_ID';
   ```

4. **随机数据**：每次执行生成的数据都不同，这是正常的
