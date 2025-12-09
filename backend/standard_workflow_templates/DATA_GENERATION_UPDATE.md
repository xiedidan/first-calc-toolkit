# 测试数据生成脚本更新说明

## 更新内容

### 1. 数据表结构变更

**之前**：直接生成 `charge_details` 表数据

**现在**：生成源表数据，由计算流程转换
- `TB_MZ_SFMXB` - 门诊收费明细表（源表）
- `TB_ZY_SFMXB` - 住院收费明细表（源表）
- `charge_details` - 统一收费明细表（由步骤1生成）

### 2. 数据流程

```
测试数据生成脚本
    ↓
TB_MZ_SFMXB (门诊源表)
TB_ZY_SFMXB (住院源表)
    ↓
步骤1: 数据准备
    ↓
charge_details (统一表)
    ↓
步骤2-4: 计算流程
```

### 3. 字段映射

#### 生成到 TB_MZ_SFMXB（门诊）

| 字段名 | 说明 | 生成规则 |
|--------|------|----------|
| YLJGDM | 医疗机构代码 | 固定值 'HOSPITAL001' |
| SFMXID | 收费明细ID | 格式：SFMX{YYYYMM}{序号6位} |
| BRZSY | 患者主索引 | 来自 patient_id |
| JZLSH | 就诊流水号 | 格式：JZ{YYYYMM}{patient_id} |
| TFBZ | 退费标志 | 固定值 '0'（非退费） |
| FYFSSJ | 费用发生时间 | 来自 charge_time |
| KDKSBM | 开单科室编码 | 来自 prescribing_dept_code |
| KDKSMC | 开单科室名称 | 从科室信息查询 |
| MXXMBM | 明细项目编码 | 来自 item_code |
| MXXMMC | 明细项目名称 | 来自 item_name |
| MXXMDJ | 明细项目单价 | amount / quantity |
| MXXMSL | 明细项目数量 | 来自 quantity |
| MXXMYSJE | 明细项目应收金额 | 来自 amount |
| MXXMSSJE | 明细项目实收金额 | 来自 amount |
| TBRQ | 数据上传时间 | 当前时间 |

#### 生成到 TB_ZY_SFMXB（住院）

字段映射与门诊表相同，只是表名不同。

### 4. 业务类别分配

- **门诊**：70% 的记录标记为门诊，插入 TB_MZ_SFMXB
- **住院**：30% 的记录标记为住院，插入 TB_ZY_SFMXB

### 5. 使用方法

#### 基本用法

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
conda activate hospital-backend

# 生成测试数据
python standard_workflow_templates/generate_test_data.py \
    --hospital-id 1 \
    --period 2025-11 \
    --record-count 500 \
    --data-source-id 2
```

#### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| --hospital-id | 是 | 医疗机构ID | 1 |
| --period | 是 | 统计周期(YYYY-MM) | 2025-11 |
| --record-count | 否 | 生成的收费记录数量 | 500 (默认100) |
| --patient-count | 否 | 患者数量 | 50 (默认50) |
| --data-source-id | 否 | 外部数据源ID | 2 (默认使用默认数据源) |
| --dry-run | 否 | 预览模式，不实际插入 | - |

#### 预览模式

```bash
# 只显示将要生成的数据，不实际插入
python standard_workflow_templates/generate_test_data.py \
    --hospital-id 1 \
    --period 2025-11 \
    --record-count 100 \
    --dry-run
```

### 6. 数据验证

脚本执行后会自动验证数据：

```
门诊收费明细汇总:
  NK: 150 条记录, 35 个患者, 总金额 12500.00 元
  WK: 120 条记录, 28 个患者, 总金额 45000.00 元
  合计: 350 条记录, 总金额 57500.00 元

住院收费明细汇总:
  NK: 80 条记录, 20 个患者, 总金额 35000.00 元
  WK: 70 条记录, 18 个患者, 总金额 52000.00 元
  合计: 150 条记录, 总金额 87000.00 元

总计: 500 条记录, 总金额 144500.00 元
```

### 7. 与计算流程的集成

#### 步骤1：数据准备

执行 `step1_data_preparation.sql` 会：
1. 清空 `charge_details` 表
2. 从 `TB_MZ_SFMXB` 提取门诊数据
3. 从 `TB_ZY_SFMXB` 提取住院数据
4. 合并到 `charge_details` 表，标记业务类别

#### 步骤2-4：计算流程

基于 `charge_details` 表进行维度统计、指标计算和价值汇总。

### 8. 数据清理

如果需要清理测试数据：

```sql
-- 清理指定周期的数据
DELETE FROM "TB_MZ_SFMXB" WHERE "FYFSSJ" >= '2025-11-01' AND "FYFSSJ" < '2025-12-01';
DELETE FROM "TB_ZY_SFMXB" WHERE "FYFSSJ" >= '2025-11-01' AND "FYFSSJ" < '2025-12-01';
DELETE FROM workload_statistics WHERE stat_month = '2025-11';

-- 清空所有测试数据
TRUNCATE TABLE "TB_MZ_SFMXB";
TRUNCATE TABLE "TB_ZY_SFMXB";
TRUNCATE TABLE charge_details;
TRUNCATE TABLE workload_statistics;
```

### 9. 常见问题

#### Q: 为什么不直接生成 charge_details？

A: 为了模拟真实的数据流程。实际生产环境中，数据来自HIS系统的门诊和住院表，需要通过ETL过程转换为统一格式。

#### Q: 如何确保生成的数据能被正确统计？

A: 脚本会优先使用维度映射中的收费项目（80%），确保大部分数据能被步骤2正确统计。

#### Q: 业务类别是如何分配的？

A: 随机分配，70%门诊，30%住院。可以根据实际需求调整比例。

#### Q: 如何验证数据生成是否成功？

A: 
1. 查看脚本输出的统计信息
2. 在数据库中查询源表记录数
3. 运行步骤1，检查 charge_details 表是否正确生成

### 10. 更新历史

- **2025-11-21**：升级脚本，生成TB_MZ_SFMXB和TB_ZY_SFMXB源表数据
- 原版本：直接生成charge_details表数据
