<template>
  <div class="system-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>

      <el-form
        ref="basicFormRef"
        :model="basicForm"
        :rules="basicRules"
        label-width="120px"
        style="max-width: 600px; padding: 20px;"
      >
        <el-form-item label="当期年月" prop="current_period">
          <el-date-picker
            v-model="basicForm.current_period"
            type="month"
            format="YYYY-MM"
            value-format="YYYY-MM"
            placeholder="选择年月"
            style="width: 100%"
          />
          <div class="form-item-tip">
            用于计算任务的默认计算周期，格式：YYYY-MM
          </div>
        </el-form-item>

        <el-form-item label="系统名称" prop="system_name">
          <el-input
            v-model="basicForm.system_name"
            placeholder="请输入系统名称"
          />
        </el-form-item>

        <el-form-item label="系统版本">
          <el-input v-model="systemVersion" disabled />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveBasicSettings" :loading="saving">
            保存设置
          </el-button>
          <el-button @click="loadSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { getSystemSettings, updateSystemSettings } from '@/api/system-settings';

const basicFormRef = ref<FormInstance>();
const saving = ref(false);

const basicForm = ref({
  current_period: '',
  system_name: '',
});

const systemVersion = ref('');

const basicRules: FormRules = {
  current_period: [
    {
      pattern: /^\d{4}-(0[1-9]|1[0-2])$/,
      message: '当期年月格式必须为YYYY-MM，例如：2025-10',
      trigger: 'blur',
    },
  ],
  system_name: [
    { max: 100, message: '系统名称不能超过100个字符', trigger: 'blur' },
  ],
};

const loadSettings = async () => {
  try {
    const data = await getSystemSettings();
    basicForm.value.current_period = data.current_period || '';
    basicForm.value.system_name = data.system_name || '';
    systemVersion.value = data.version || '';
  } catch (error) {
    ElMessage.error('加载设置失败');
    console.error(error);
  }
};

const saveBasicSettings = async () => {
  if (!basicFormRef.value) return;

  await basicFormRef.value.validate(async (valid) => {
    if (!valid) return;

    saving.value = true;
    try {
      const updateData: any = {
        current_period: basicForm.value.current_period || null,
        system_name: basicForm.value.system_name || null,
      };

      await updateSystemSettings(updateData);
      ElMessage.success('保存成功');
      await loadSettings();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '保存失败';
      ElMessage.error(errorMsg);
      console.error(error);
    } finally {
      saving.value = false;
    }
  });
};

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.system-settings {
  padding: 0;
  width: 100%;
  height: 100%;
}

.settings-card {
  width: 100%;
  height: 100%;
}

.settings-card :deep(.el-card__body) {
  height: calc(100% - 60px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
