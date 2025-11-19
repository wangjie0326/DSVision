import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host:'127.0.0.1',
    port:5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // Flask 后端运行地址
        changeOrigin: true,
        rewrite: (path) => {
          // /api/llm/* /api/dsl/* /api/code/* 和其他新 API 保留 /api 前缀
          if (path.startsWith('/api/llm') || path.startsWith('/api/dsl') || path.startsWith('/api/code')) {
            return path
          }
          // 旧 API (/api/structure 等) 去掉 /api 前缀
          return path.replace(/^\/api/, '')
        }
      }
    }
  }
})

