import { defineConfig } from 'vite'
import tsConfigPaths from 'vite-tsconfig-paths'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import { resolve } from 'path'

export default defineConfig({
  root: 'frontend',
  publicDir: 'frontend/public',
  server: {
    port: 3000,
  },
  plugins: [
    tanstackRouter(),
    react(),
    tailwindcss(),
    tsConfigPaths(),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'frontend/src'),
    },
  },
})