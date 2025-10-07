// pants/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],

  // ✅ Use the actual frontend folder as the root
  root: './frontend',

  // ✅ Keep public assets inside ./frontend/public
  publicDir: './public',

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },

  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },

  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
})
