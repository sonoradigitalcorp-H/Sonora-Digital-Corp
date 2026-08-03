import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 8770, host: '0.0.0.0' },
  preview: { port: 8770, host: '0.0.0.0' }
})
