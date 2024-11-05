import { defineConfig } from 'vite'
import { resolve } from "path";
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: "/static/",
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  server: {
    watch: {
      usePolling: true,
    }
  },
  build: {
    manifest: "manifest.json",
    outDir: resolve("./frontend/dist"),
    rollupOptions: {
      input: {
        main: resolve("./frontend/src/main.js"),
      },
    },
  },
})
