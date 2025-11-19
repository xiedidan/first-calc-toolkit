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

/* 确保遮罩层覆盖整个视口 */
.el-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 2000 !important;
}

/* 修复模态框在页面滚动时的定位问题 */
.el-overlay-dialog {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  display: flex !important;
  align-items: flex-start !important;
  justify-content: center !important;
  padding: 5vh 0 !important;
  overflow-y: auto !important;
  pointer-events: none !important;
}

.el-overlay-dialog .el-dialog {
  pointer-events: auto !important;
}

.el-dialog {
  position: relative !important;
  margin: 0 auto !important;
  display: flex !important;
  flex-direction: column !important;
}

/* 全高度对话框 */
.full-height-dialog.el-dialog {
  height: calc(100vh - 10vh) !important;
  min-height: calc(100vh - 10vh) !important;
  max-height: calc(100vh - 10vh) !important;
}

.full-height-dialog .el-dialog__body {
  overflow-y: auto !important;
  flex: 1 !important;
}

/* 确保对话框主体可滚动并填充空间 */
.el-dialog__body {
  overflow-y: auto !important;
}

/* 对话框头部和底部固定 */
.el-dialog__header {
  flex-shrink: 0 !important;
}

.el-dialog__footer {
  flex-shrink: 0 !important;
}
</style>
