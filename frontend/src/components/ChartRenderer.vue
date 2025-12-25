<template>
  <div class="chart-renderer">
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>图表加载中...</span>
    </div>
    <div v-else-if="error" class="chart-error">
      <el-icon><WarningFilled /></el-icon>
      <span>{{ error }}</span>
    </div>
    <div v-else ref="chartRef" class="chart-container" :style="containerStyle"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

// 图表类型定义
export type ChartType = 'line' | 'bar' | 'pie' | 'scatter' | 'area'

// 图表数据接口
export interface ChartData {
  labels?: string[]
  datasets?: { name: string; data: number[]; color?: string }[]
  items?: { name: string; value: number; color?: string }[]
}

// 图表配置接口
export interface ChartConfig {
  title?: string
  subtitle?: string
  xAxisLabel?: string
  yAxisLabel?: string
  showLegend?: boolean
  showTooltip?: boolean
  colors?: string[]
}

const props = withDefaults(defineProps<{
  type: ChartType
  data: ChartData
  config?: ChartConfig
  width?: string | number
  height?: string | number
}>(), {
  config: () => ({}),
  width: '100%',
  height: 300
})

const emit = defineEmits<{
  (e: 'click', params: any): void
  (e: 'ready', chart: echarts.ECharts): void
}>()

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
let chartInstance: echarts.ECharts | null = null

const defaultColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b8d0']

const containerStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

const generateOption = (): echarts.EChartsOption => {
  const { type, data, config } = props
  const colors = config?.colors || defaultColors

  const baseOption: echarts.EChartsOption = {
    color: colors,
    title: config?.title ? { text: config.title, subtext: config?.subtitle, left: 'center' } : undefined,
    tooltip: config?.showTooltip !== false ? { trigger: type === 'pie' ? 'item' : 'axis', axisPointer: type !== 'pie' ? { type: 'shadow' } : undefined } : undefined,
    legend: config?.showLegend !== false ? { bottom: 10, type: 'scroll' } : undefined
  }

  switch (type) {
    case 'line':
      return { ...baseOption, xAxis: { type: 'category', data: data.labels || [], name: config?.xAxisLabel, axisLabel: { rotate: data.labels && data.labels.length > 10 ? 45 : 0 } }, yAxis: { type: 'value', name: config?.yAxisLabel }, series: (data.datasets || []).map(ds => ({ name: ds.name, type: 'line', data: ds.data, smooth: true, itemStyle: ds.color ? { color: ds.color } : undefined })) }
    case 'area':
      return { ...baseOption, xAxis: { type: 'category', data: data.labels || [], name: config?.xAxisLabel, boundaryGap: false, axisLabel: { rotate: data.labels && data.labels.length > 10 ? 45 : 0 } }, yAxis: { type: 'value', name: config?.yAxisLabel }, series: (data.datasets || []).map(ds => ({ name: ds.name, type: 'line', data: ds.data, smooth: true, areaStyle: {}, itemStyle: ds.color ? { color: ds.color } : undefined })) }
    case 'bar':
      return { ...baseOption, xAxis: { type: 'category', data: data.labels || [], name: config?.xAxisLabel, axisLabel: { rotate: data.labels && data.labels.length > 6 ? 45 : 0 } }, yAxis: { type: 'value', name: config?.yAxisLabel }, series: (data.datasets || []).map(ds => ({ name: ds.name, type: 'bar', data: ds.data, itemStyle: ds.color ? { color: ds.color } : undefined })) }
    case 'pie':
      return { ...baseOption, series: [{ type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: true, itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 }, label: { show: true, formatter: '{b}: {d}%' }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } }, data: (data.items || []).map(item => ({ name: item.name, value: item.value, itemStyle: item.color ? { color: item.color } : undefined })) }] }
    case 'scatter':
      return { ...baseOption, xAxis: { type: 'value', name: config?.xAxisLabel }, yAxis: { type: 'value', name: config?.yAxisLabel }, series: (data.datasets || []).map(ds => ({ name: ds.name, type: 'scatter', data: ds.data, itemStyle: ds.color ? { color: ds.color } : undefined })) }
    default:
      return baseOption
  }
}

const initChart = async () => {
  if (!chartRef.value) return
  loading.value = true
  error.value = null
  try {
    await nextTick()
    if (chartInstance) chartInstance.dispose()
    chartInstance = echarts.init(chartRef.value)
    const option = generateOption()
    chartInstance.setOption(option)
    chartInstance.on('click', (params: any) => { emit('click', params) })
    emit('ready', chartInstance)
  } catch (e: any) {
    error.value = e.message || '图表渲染失败'
    console.error('Chart render error:', e)
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartInstance) { initChart(); return }
  try {
    const option = generateOption()
    chartInstance.setOption(option, true)
  } catch (e: any) {
    error.value = e.message || '图表更新失败'
    console.error('Chart update error:', e)
  }
}

const resize = () => { chartInstance?.resize() }

watch(() => [props.type, props.data, props.config], () => { updateChart() }, { deep: true })
watch(() => [props.width, props.height], () => { nextTick(() => resize()) })

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  initChart()
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => { resize() })
    resizeObserver.observe(chartRef.value)
  }
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  if (chartInstance) { chartInstance.dispose(); chartInstance = null }
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  window.removeEventListener('resize', resize)
})

defineExpose({ resize, getChart: () => chartInstance })
</script>

<style scoped>
.chart-renderer { width: 100%; position: relative; }
.chart-container { min-height: 200px; }
.chart-loading, .chart-error { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; color: #909399; gap: 8px; }
.chart-loading .el-icon { font-size: 24px; color: #409eff; }
.chart-error { color: #f56c6c; }
.chart-error .el-icon { font-size: 24px; }
</style>
