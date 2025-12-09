<template>
  <el-autocomplete
    :model-value="modelValue"
    @update:model-value="handleInput"
    :fetch-suggestions="querySearch"
    :placeholder="placeholder"
    :clearable="true"
    @select="handleSelect"
    @clear="handleClear"
    style="width: 100%"
    value-key="label"
  >
    <template #default="{ item }">
      <div class="user-option">
        <span class="user-name">{{ item.name }}</span>
        <span class="user-username">{{ item.username }}</span>
      </div>
    </template>
  </el-autocomplete>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getUserList, type UserInfo } from '@/api/user'

interface Props {
  modelValue: string
  userId?: number | null
  placeholder?: string
  required?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'update:userId', value: number | null): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入或选择用户',
  required: false
})

const emit = defineEmits<Emits>()

// 用户列表缓存
const userListCache = ref<UserInfo[]>([])
const cacheTime = ref<number>(0)
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

// 搜索用户
const querySearch = async (queryString: string, cb: (results: any[]) => void) => {
  // 如果输入为空，返回空列表
  if (!queryString) {
    cb([])
    return
  }

  try {
    // 检查缓存是否有效
    const now = Date.now()
    if (userListCache.value.length > 0 && now - cacheTime.value < CACHE_DURATION) {
      // 使用缓存数据进行本地过滤
      const results = filterUsers(userListCache.value, queryString)
      cb(results)
      return
    }

    // 从服务器获取用户列表
    const response = await getUserList({
      page: 1,
      size: 100,
      keyword: queryString
    })

    // 更新缓存
    userListCache.value = response.items
    cacheTime.value = now

    // 格式化结果
    const results = response.items.map(user => ({
      value: user.id,
      label: user.name,
      name: user.name,
      username: user.username
    }))

    cb(results)
  } catch (error) {
    console.error('Failed to fetch users:', error)
    cb([])
  }
}

// 本地过滤用户
const filterUsers = (users: UserInfo[], query: string) => {
  const lowerQuery = query.toLowerCase()
  return users
    .filter(user => 
      user.name.toLowerCase().includes(lowerQuery) ||
      user.username.toLowerCase().includes(lowerQuery)
    )
    .map(user => ({
      value: user.id,
      label: user.name,
      name: user.name,
      username: user.username
    }))
}

// 处理输入
const handleInput = (value: string) => {
  emit('update:modelValue', value)
  // 如果是手动输入（不是选择），清除userId
  if (value !== props.modelValue) {
    emit('update:userId', null)
  }
}

// 处理选择
const handleSelect = (item: any) => {
  emit('update:modelValue', item.label)
  emit('update:userId', item.value)
}

// 处理清除
const handleClear = () => {
  emit('update:modelValue', '')
  emit('update:userId', null)
}
</script>

<style scoped>
.user-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-name {
  font-weight: 500;
}

.user-username {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}
</style>
