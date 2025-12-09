<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建分类任务"
    width="600px"
    :close-on-click-modal="false"
    append-to-body
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="任务名称" prop="task_name">
        <el-input
          v-model="formData.task_name"
          placeholder="请输入任务名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="模型版本" prop="model_version_id">
        <el-select
          v-model="formData.model_version_id"
          placeholder="请选择模型版本"
          style="width: 100%"
          @change="handleVersionChange"
        >
          <el-option
            v-for="version in modelVersions"
            :key="version.id"
            :label="`${version.name} (${version.is_active ? '激活' : '未激活'})`"
            :value="version.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="收费类别" prop="charge_categories">
        <div v-if="loadingCategories" class="form-tip">加载中...</div>
        <div v-else-if="chargeCategories.length === 0" class="form-tip">暂无收费类别数据</div>
        <el-checkbox-group v-else v-model="formData.charge_categories">
          <el-checkbox
            v-for="category in chargeCategories"
            :key="category"
            :label="category"
          >
            {{ category }}
          </el-checkbox>
        </el-checkbox-group>
        <div class="form-tip">
          至少选择一个收费类别（从收费项目表提取）
        </div>
      </el-form-item>

      <el-form-item v-if="leafDimensionCount > 0" label="末级维度数量">
        <el-tag type="info">{{ leafDimensionCount }} 个</el-tag>
        <span class="form-tip" style="margin-left: 10px">
          AI将从这些维度中选择最合适的分类
        </span>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          创建任务
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { createClassificationTask, getChargeCategories } from '@/api/classification-tasks';
import { getModelVersions, getModelNodes, type ModelVersion } from '@/api/model';

interface Props {
  visible: boolean;
}

interface Emits {
  (e: 'update:visible', value: boolean): void;
  (e: 'success'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const loading = ref(false);
const modelVersions = ref<ModelVersion[]>([]);
const leafDimensionCount = ref(0);
const chargeCategories = ref<string[]>([]);
const loadingCategories = ref(false);

// 表单数据
const formData = reactive({
  task_name: '',
  model_version_id: null as number | null,
  charge_categories: [] as string[]
});

// 表单验证规则
const rules: FormRules = {
  task_name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 1, max: 100, message: '任务名称长度在1-100个字符', trigger: 'blur' }
  ],
  model_version_id: [
    { required: true, message: '请选择模型版本', trigger: 'change' }
  ],
  charge_categories: [
    {
      type: 'array',
      required: true,
      message: '请至少选择一个收费类别',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('请至少选择一个收费类别'));
        } else {
          callback();
        }
      }
    }
  ]
};

// 监听visible变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val;
  if (val) {
    loadModelVersions();
    loadChargeCategories();
  }
});

watch(dialogVisible, (val) => {
  emit('update:visible', val);
});

// 加载模型版本列表
const loadModelVersions = async () => {
  try {
    const response = await getModelVersions();
    modelVersions.value = response.items;
  } catch (error) {
    console.error('加载模型版本失败:', error);
    ElMessage.error('加载模型版本失败');
  }
};

// 加载收费类别列表
const loadChargeCategories = async () => {
  loadingCategories.value = true;
  try {
    chargeCategories.value = await getChargeCategories();
  } catch (error) {
    console.error('加载收费类别失败:', error);
    ElMessage.error('加载收费类别失败');
  } finally {
    loadingCategories.value = false;
  }
};

// 模型版本变化时加载末级维度数量
const handleVersionChange = async (versionId: number) => {
  if (!versionId) {
    leafDimensionCount.value = 0;
    return;
  }

  try {
    const response = await getModelNodes({ version_id: versionId });
    // 统计末级维度（is_leaf = true）
    leafDimensionCount.value = response.items.filter(node => node.is_leaf).length;
  } catch (error) {
    console.error('加载维度信息失败:', error);
    leafDimensionCount.value = 0;
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    loading.value = true;

    await createClassificationTask({
      task_name: formData.task_name,
      model_version_id: formData.model_version_id!,
      charge_categories: formData.charge_categories
    });

    ElMessage.success('任务创建成功，正在后台处理');
    emit('success');
    handleClose();
  } catch (error: any) {
    console.error('创建任务失败:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error('创建任务失败');
    }
  } finally {
    loading.value = false;
  }
};

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields();
  formData.task_name = '';
  formData.model_version_id = null;
  formData.charge_categories = [];
  leafDimensionCount.value = 0;
  dialogVisible.value = false;
};
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
