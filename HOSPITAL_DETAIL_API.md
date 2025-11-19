# 全院汇总明细API

## 功能说明

为"全院汇总"这一行添加"查看明细"功能，显示各维度汇总了所有科室的数据。

## API端点

### GET /api/results/hospital-detail

获取全院汇总的详细业务价值数据

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

#### 响应格式

与单科室明细API (`/api/results/detail`) 相同的格式：

```json
{
  "department_id": 0,
  "department_name": "全院汇总",
  "period": "2025-10",
  "sequences": [...],
  "doctor": [...],
  "nurse": [...],
  "tech": [...]
}
```

## 数据计算逻辑

### 1. 汇总所有科室的数据

对于每个节点（序列或维度），汇总所有科室的数据：

```
全院节点工作量 = Σ(该节点在所有科室的工作量)
全院节点价值 = Σ(该节点在所有科室的价值)
```

### 2. 构建树形结构

使用与单科室明细相同的树形结构：

```
序列
├─ 一级维度
│  ├─ 二级维度（叶子）
│  └─ 二级维度（叶子）
└─ 一级维度
   └─ 二级维度（叶子）
```

### 3. 计算占比

各维度在全院范围内的占比：

```
维度占比 = 该维度全院价值 / 同级所有维度全院价值总和 × 100%
```

## 示例

假设有2个科室：

### 科室A
- 门诊诊察：工作量=1000, 价值=50000
- 住院诊察：工作量=500, 价值=75000

### 科室B
- 门诊诊察：工作量=800, 价值=40000
- 住院诊察：工作量=600, 价值=90000

### 全院汇总明细
- 门诊诊察：工作量=1800, 价值=90000, 占比=35.3%
- 住院诊察：工作量=1100, 价值=165000, 占比=64.7%

## 前端集成

### 1. 汇总表中添加操作按钮

在"全院汇总"这一行的操作列添加"查看明细"按钮：

```vue
<template>
  <el-table :data="tableData">
    <!-- 其他列 -->
    <el-table-column label="操作">
      <template #default="{ row }">
        <el-button 
          v-if="row.department_id === 0"
          type="text" 
          @click="viewHospitalDetail(row)">
          查看明细
        </el-button>
        <el-button 
          v-else
          type="text" 
          @click="viewDeptDetail(row)">
          查看明细
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  methods: {
    viewHospitalDetail(row) {
      // 跳转到全院汇总明细页面
      this.$router.push({
        name: 'HospitalDetail',
        query: {
          taskId: this.currentTaskId,
          period: this.currentPeriod
        }
      })
    },
    
    viewDeptDetail(row) {
      // 跳转到科室明细页面
      this.$router.push({
        name: 'DepartmentDetail',
        query: {
          deptId: row.department_id,
          taskId: this.currentTaskId
        }
      })
    }
  }
}
</script>
```

### 2. 创建全院明细页面

可以复用现有的科室明细页面组件，只需要：

1. 判断 `deptId` 是否为 0 或不存在
2. 如果是全院汇总，调用 `/api/results/hospital-detail`
3. 如果是单科室，调用 `/api/results/detail`

```vue
<template>
  <div>
    <h2>{{ isHospital ? '全院汇总' : departmentName }} - 业务价值明细</h2>
    
    <!-- 复用相同的表格组件 -->
    <ValueDetailTable 
      :doctor-data="doctorData"
      :nurse-data="nurseData"
      :tech-data="techData"
    />
  </div>
</template>

<script>
export default {
  computed: {
    isHospital() {
      return !this.$route.query.deptId || this.$route.query.deptId === '0'
    }
  },
  
  methods: {
    async loadData() {
      if (this.isHospital) {
        // 加载全院汇总明细
        const response = await this.$api.get('/results/hospital-detail', {
          params: { task_id: this.$route.query.taskId }
        })
        this.processData(response.data)
      } else {
        // 加载科室明细
        const response = await this.$api.get('/results/detail', {
          params: {
            dept_id: this.$route.query.deptId,
            task_id: this.$route.query.taskId
          }
        })
        this.processData(response.data)
      }
    }
  }
}
</script>
```

## 测试

### 1. 测试API
```bash
python backend/test_hospital_detail_api.py
```

### 2. 手动测试

```bash
# 启动后端服务
cd backend
python -m uvicorn app.main:app --reload

# 访问API
curl "http://localhost:8000/api/results/hospital-detail?task_id=YOUR_TASK_ID"
```

### 3. 验证数据

检查返回的数据：
- ✅ department_id 应该为 0
- ✅ department_name 应该为 "全院汇总"
- ✅ 各维度的工作量和价值应该是所有科室的总和
- ✅ 占比应该正确计算
- ✅ 树形结构应该完整

## 注意事项

1. **性能考虑**
   - 全院汇总需要查询所有科室的数据
   - 数据量大时可能较慢
   - 考虑添加缓存或分页

2. **数据一致性**
   - 使用与单科室明细相同的计算逻辑
   - 确保汇总算法正确

3. **权重处理**
   - 权重不汇总，取第一个科室的权重值
   - 因为权重是模型定义的，所有科室应该相同

4. **业务导向**
   - 从模型节点读取，不从计算结果读取
   - 确保显示正确的业务导向信息

## 相关文件

- `backend/app/api/calculation_tasks.py` - API实现
- `backend/test_hospital_detail_api.py` - API测试脚本
- `frontend/src/views/Results.vue` - 前端汇总表页面（需要修改）
- `frontend/src/views/HospitalDetail.vue` - 前端全院明细页面（需要创建）

## 后续优化

1. **缓存机制**：缓存全院汇总数据，提高性能
2. **增量更新**：只更新变化的科室数据
3. **导出功能**：支持导出全院汇总明细
4. **对比分析**：支持多个周期的全院数据对比
