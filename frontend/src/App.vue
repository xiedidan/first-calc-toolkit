<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 应用根组件
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
