import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将 node_modules 中的包分组
          if (id.includes('node_modules')) {
            // Element Plus 单独打包
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
            // Vue 核心库单独打包（避免与其他 vue 相关包混在一起导致循环依赖）
            if (id.includes('/vue/') || id.includes('/@vue/')) {
              return 'vue-core'
            }
            // Pinia 单独打包
            if (id.includes('pinia')) {
              return 'pinia'
            }
            // Vue Router 单独打包
            if (id.includes('vue-router')) {
              return 'vue-router'
            }
            // 其他第三方库
            return 'vendor'
          }
        }
      }
    }
  }
})
