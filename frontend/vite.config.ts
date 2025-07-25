import { defineConfig } from 'vite'
import tsConfigPaths from 'vite-tsconfig-paths'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

export default defineConfig({
  server: {
    port: 3000,
  },
  plugins: [
    tanstackRouter(),
    react(),
    tailwindcss(),
    tsConfigPaths(),
  ],
})