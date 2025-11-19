<template>
  <div class="data-source-management">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新建数据源
      </el-button>
      
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索数据源名称"
          clearable
          @clear="loadDataSources"
          @keyup.enter="loadDataSources"
          style="width: 300px"
        >
          <template #append>
            <el-button :icon="Search" @click="loadDataSources" />
          </template>
        </el-input>
      </div>
    </div>

    <!-- 数据源列表 -->
    <el-table
      :data="dataSources"
      v-loading="loading"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="name" label="数据源名称" min-width="150" />
      <el-table-column prop="db_type" label="数据库类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getDbTypeTagType(row.db_type)">
            {{ getDbTypeLabel(row.db_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="host" label="主机地址" min-width="150" />
      <el-table-column prop="port" label="端口" width="80" />
      <el-table-column prop="database_name" label="数据库名" min-width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag
            :type="getStatusTagType(row.connection_status)"
            size="small"
          >
            {{ getStatusLabel(row.connection_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="默认" width="80" align="center">
        <template #default="{ row }">
          <el-icon v-if="row.is_default" color="#67C23A" :size="20">
            <Check />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_enabled"
            @change="handleToggle(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            link
            @click="handleTest(row)"
          >
            测试连接
          </el-button>
          <el-button
            type="primary"
            size="small"
            link
            @click="handleSetDefault(row)"
            :disabled="row.is_default"
          >
            设为默认
          </el-button>
          <el-button
            type="primary"
            size="small"
            link
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            link
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.size"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="loadDataSources"
      @current-change="loadDataSources"
      style="margin-top: 20px; justify-content: flex-end"
    />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称" />
        </el-form-item>

        <el-form-item label="数据库类型" prop="db_type">
          <el-select
            v-model="form.db_type"
            placeholder="请选择数据库类型"
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MySQL" value="mysql" />
            <el-option label="SQL Server" value="sqlserver" />
            <el-option label="Oracle" value="oracle" />
          </el-select>
        </el-form-item>

        <el-form-item label="主机地址" prop="host">
          <el-input v-model="form.host" placeholder="例如：192.168.1.100" />
        </el-form-item>

        <el-form-item label="端口号" prop="port">
          <el-input-number
            v-model="form.port"
            :min="1"
            :max="65535"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="数据库名称" prop="database_name">
          <el-input v-model="form.database_name" placeholder="请输入数据库名称" />
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
          <div v-if="isEdit" class="form-item-tip">
            留空表示不修改密码
          </div>
        </el-form-item>

        <el-form-item label="Schema名称">
          <el-input
            v-model="form.schema_name"
            placeholder="可选，PostgreSQL/Oracle使用"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入数据源描述"
          />
        </el-form-item>

        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>

        <el-collapse>
          <el-collapse-item title="高级设置" name="advanced">
            <el-form-item label="最小连接数">
              <el-input-number
                v-model="form.pool_size_min"
                :min="1"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="最大连接数">
              <el-input-number
                v-model="form.pool_size_max"
                :min="1"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="连接超时(秒)">
              <el-input-number
                v-model="form.pool_timeout"
                :min="1"
                :max="300"
                style="width: 100%"
              />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <div class="footer-left">
            <el-button
              type="warning"
              @click="handleTestInDialog"
              :loading="testing"
            >
              测试连接
            </el-button>
          </div>
          <div class="footer-right">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              确定
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { Plus, Search, Check } from '@element-plus/icons-vue';
import {
  getDataSources,
  createDataSource,
  updateDataSource,
  deleteDataSource,
  testDataSource,
  testConnectionWithConfig,
  toggleDataSource,
  setDefaultDataSource,
  type DataSource,
  type DataSourceCreate,
  type DataSourceUpdate,
} from '@/api/data-sources';

const loading = ref(false);
const submitting = ref(false);
const testing = ref(false);
const dialogVisible = ref(false);
const isEdit = ref(false);
const editingId = ref<number | null>(null);
const searchKeyword = ref('');

const dataSources = ref<DataSource[]>([]);
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
});

const formRef = ref<FormInstance>();
const form = ref<DataSourceCreate>({
  name: '',
  db_type: 'postgresql',
  host: '',
  port: 5432,
  database_name: '',
  username: '',
  password: '',
  schema_name: '',
  description: '',
  is_default: false,
  is_enabled: true,
  pool_size_min: 2,
  pool_size_max: 10,
  pool_timeout: 30,
});

const formRules: FormRules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口号', trigger: 'blur' }],
  database_name: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    {
      required: true,
      validator: (rule, value, callback) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入密码'));
        } else {
          callback();
        }
      },
      trigger: 'blur',
    },
  ],
};

const dialogTitle = computed(() => (isEdit.value ? '编辑数据源' : '新建数据源'));

const getDbTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    postgresql: 'PostgreSQL',
    mysql: 'MySQL',
    sqlserver: 'SQL Server',
    oracle: 'Oracle',
  };
  return labels[type] || type;
};

const getDbTypeTagType = (type: string) => {
  const types: Record<string, any> = {
    postgresql: 'primary',
    mysql: 'success',
    sqlserver: 'warning',
    oracle: 'danger',
  };
  return types[type] || '';
};

const getStatusLabel = (status?: string) => {
  const labels: Record<string, string> = {
    online: '在线',
    offline: '离线',
    error: '错误',
  };
  return labels[status || 'offline'] || '未知';
};

const getStatusTagType = (status?: string) => {
  const types: Record<string, any> = {
    online: 'success',
    offline: 'info',
    error: 'danger',
  };
  return types[status || 'offline'] || 'info';
};

const loadDataSources = async () => {
  loading.value = true;
  try {
    const data = await getDataSources({
      page: pagination.page,
      size: pagination.size,
      keyword: searchKeyword.value || undefined,
    });
    dataSources.value = data.items;
    pagination.total = data.total;
  } catch (error) {
    ElMessage.error('加载数据源列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const showCreateDialog = () => {
  isEdit.value = false;
  editingId.value = null;
  dialogVisible.value = true;
};

const handleEdit = (row: DataSource) => {
  isEdit.value = true;
  editingId.value = row.id;
  form.value = {
    name: row.name,
    db_type: row.db_type,
    host: row.host,
    port: row.port,
    database_name: row.database_name,
    username: row.username,
    password: '',
    schema_name: row.schema_name || '',
    description: row.description || '',
    is_default: row.is_default,
    is_enabled: row.is_enabled,
    pool_size_min: row.pool_size_min,
    pool_size_max: row.pool_size_max,
    pool_timeout: row.pool_timeout,
  };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      if (isEdit.value && editingId.value) {
        const updateData: DataSourceUpdate = { ...form.value };
        if (!updateData.password) {
          delete updateData.password;
        }
        await updateDataSource(editingId.value, updateData);
        ElMessage.success('更新成功');
      } else {
        await createDataSource(form.value);
        ElMessage.success('创建成功');
      }
      dialogVisible.value = false;
      await loadDataSources();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '操作失败';
      ElMessage.error(errorMsg);
      console.error(error);
    } finally {
      submitting.value = false;
    }
  });
};

const handleDelete = async (row: DataSource) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据源"${row.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await deleteDataSource(row.id);
    ElMessage.success('删除成功');
    await loadDataSources();
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.detail || '删除失败';
      ElMessage.error(errorMsg);
      console.error(error);
    }
  }
};

const handleTest = async (row: DataSource) => {
  const loading = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0,
  });

  try {
    const result = await testDataSource(row.id);
    loading.close();

    if (result.success) {
      ElMessage.success(`连接成功！耗时：${result.duration_ms}ms`);
    } else {
      ElMessage.error(`连接失败：${result.error}`);
    }
  } catch (error: any) {
    loading.close();
    const errorMsg = error.response?.data?.detail || '测试失败';
    ElMessage.error(errorMsg);
    console.error(error);
  }
};

const handleToggle = async (row: DataSource) => {
  try {
    await toggleDataSource(row.id);
    ElMessage.success(row.is_enabled ? '已启用' : '已禁用');
    await loadDataSources();
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '操作失败';
    ElMessage.error(errorMsg);
    row.is_enabled = !row.is_enabled;
    console.error(error);
  }
};

const handleSetDefault = async (row: DataSource) => {
  try {
    await setDefaultDataSource(row.id);
    ElMessage.success('设置成功');
    await loadDataSources();
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '设置失败';
    ElMessage.error(errorMsg);
    console.error(error);
  }
};

const handleTestInDialog = async () => {
  if (!formRef.value) return;

  // 验证必填字段
  try {
    await formRef.value.validate();
  } catch (error) {
    ElMessage.warning('请先填写完整的连接信息');
    return;
  }

  // 编辑模式下，如果密码为空，提示用户
  if (isEdit.value && !form.value.password) {
    ElMessage.warning('编辑模式下测试连接需要输入密码');
    return;
  }

  testing.value = true;
  const loadingMsg = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0,
  });

  try {
    // 无论新建还是编辑模式，都使用表单中的当前配置进行测试
    const result = await testConnectionWithConfig(form.value);
    
    loadingMsg.close();

    if (result.success) {
      ElMessage.success(`连接成功！耗时：${result.duration_ms}ms`);
    } else {
      ElMessage.error(`连接失败：${result.error}`);
    }
  } catch (error: any) {
    loadingMsg.close();
    const errorMsg = error.response?.data?.detail || '测试失败';
    ElMessage.error(errorMsg);
    console.error(error);
  } finally {
    testing.value = false;
  }
};

const resetForm = () => {
  formRef.value?.resetFields();
  form.value = {
    name: '',
    db_type: 'postgresql',
    host: '',
    port: 5432,
    database_name: '',
    username: '',
    password: '',
    schema_name: '',
    description: '',
    is_default: false,
    is_enabled: true,
    pool_size_min: 2,
    pool_size_max: 10,
    pool_timeout: 30,
  };
};

onMounted(() => {
  loadDataSources();
});
</script>

<style scoped>
.data-source-management {
  width: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 10px;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.footer-left {
  /* 不设置flex: 1，让按钮保持自然宽度 */
}

.footer-right {
  display: flex;
  gap: 10px;
  margin-left: auto;
}
</style>
