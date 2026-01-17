<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

// 全局滚轮事件处理：让表格区域的垂直滚轮事件穿透到正确的滚动容器
const handleTableWheel = (e: WheelEvent) => {
  const target = e.target as HTMLElement
  
  // 检查事件是否来自表格内部
  const table = target.closest('.el-table')
  if (!table) return
  
  // 检查表格是否有设置 max-height（需要内部滚动的表格）
  const tableWrapper = table.querySelector('.el-table__body-wrapper') as HTMLElement
  if (tableWrapper) {
    const maxHeight = tableWrapper.style.maxHeight || 
                      window.getComputedStyle(tableWrapper).maxHeight
    if (maxHeight && maxHeight !== 'none') {
      // 有 max-height 的表格，让它自己处理滚动
      return
    }
  }
  
  // 检查是否在对话框内
  const dialog = target.closest('.el-dialog')
  if (dialog) {
    // 对话框内的表格，滚动对话框的 body
    const dialogBody = dialog.querySelector('.el-dialog__body') as HTMLElement
    if (dialogBody) {
      dialogBody.scrollTop += e.deltaY
    }
    return
  }
  
  // 页面上的表格，滚动 layout-main
  const scrollContainer = document.querySelector('.layout-main') as HTMLElement
  if (scrollContainer) {
    scrollContainer.scrollTop += e.deltaY
  }
}

onMounted(() => {
  document.addEventListener('wheel', handleTableWheel, { passive: true })
})

onUnmounted(() => {
  document.removeEventListener('wheel', handleTableWheel)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
}

/* ========== Element Plus 对话框全局修复 ========== */
/* 问题：页面滚动时打开对话框，对话框可能定位到视口外 */

/* 确保遮罩层覆盖整个视口（固定定位） */
.el-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
}

/* 对话框容器：固定定位 + 居中 + 可滚动 */
.el-overlay-dialog {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: flex-start !important;
  justify-content: center !important;
  padding-top: 10vh !important;
  padding-bottom: 10vh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

/* 对话框本身：相对定位，不受页面滚动影响 */
.el-dialog {
  position: relative !important;
  margin: 0 auto !important;
  display: flex !important;
  flex-direction: column !important;
  max-height: 80vh !important;
  transform: none !important;
}

/* 对话框主体可滚动 */
.el-dialog__body {
  overflow-y: auto !important;
  flex: 1 1 auto !important;
  max-height: calc(80vh - 120px) !important;
}

/* 对话框头部和底部固定高度 */
.el-dialog__header {
  flex-shrink: 0 !important;
}

.el-dialog__footer {
  flex-shrink: 0 !important;
}

/* ========== 全高度对话框（用于日志等需要更多空间的场景） ========== */
.full-height-dialog.el-dialog {
  max-height: 85vh !important;
}

.full-height-dialog .el-dialog__body {
  max-height: calc(85vh - 120px) !important;
  flex: 1 !important;
}

/* ========== 确保页面滚动正常 ========== */
/* 防止双重滚动条：html/body 不滚动，只有内容区域滚动 */
html {
  overflow: hidden;
  height: 100%;
}

body {
  overflow: hidden;
  height: 100%;
}

/* 确保主内容区域可滚动 */
.main-content,
.el-main {
  overflow-y: auto !important;
}

/* ========== 全局紧凑样式 ========== */
/* 缩小全局字体 */
html {
  font-size: 13px;
}

/* 表格行更紧凑 */
.el-table th.el-table__cell,
.el-table td.el-table__cell {
  padding: 6px 0;
}

/* 修复表格区域鼠标滚轮无法滚动页面的问题 */
/* Element Plus 表格默认会捕获滚轮事件用于水平滚动，导致页面无法垂直滚动 */
/* 解决方案：只对页面上的表格（非对话框内）应用 overflow 修复 */

/* 页面上的表格（排除对话框内的表格）：保留横向滚动，禁用纵向滚动 */
.layout-main .el-table .el-table__body-wrapper {
  overflow-x: auto !important;
  overflow-y: visible !important;
}

.layout-main .el-table__inner-wrapper {
  overflow-x: auto !important;
  overflow-y: visible !important;
}

.layout-main .el-table .el-scrollbar__wrap {
  overflow-x: auto !important;
  overflow-y: visible !important;
}

/* 修复表格固定列导致页面无法滚动的问题 */
/* 只对页面上的表格应用 pointer-events 穿透 */
.layout-main .el-table__fixed,
.layout-main .el-table__fixed-right {
  pointer-events: none;
}
.layout-main .el-table__fixed *,
.layout-main .el-table__fixed-right * {
  pointer-events: auto;
}

/* 页面上表格固定列的滚动条也保留横向滚动 */
.layout-main .el-table__fixed .el-scrollbar__wrap,
.layout-main .el-table__fixed-right .el-scrollbar__wrap {
  overflow-x: auto !important;
  overflow-y: visible !important;
}

/* 表单项间距更紧凑 */
.el-form-item {
  margin-bottom: 14px;
}

/* 卡片内边距更紧凑 */
.el-card__header {
  padding: 12px 16px;
}

.el-card__body {
  padding: 14px;
}

/* 菜单项更紧凑 */
.el-menu-item {
  height: 44px;
  line-height: 44px;
  font-size: 13px;
}

.el-sub-menu__title {
  height: 44px;
  line-height: 44px;
  font-size: 13px;
}
</style>
