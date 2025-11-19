import { defineConfig } from 'vite';
import tsConfigPaths from 'vite-tsconfig-paths';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { tanstackRouter } from '@tanstack/router-plugin/vite';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: '.',
  publicDir: 'public',
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/graphql': {
        target: 'http://web:5000',
        changeOrigin: true,
        rewrite: path => path,
      },
      '/auth': {
        target: 'http://web:5000',
        changeOrigin: true,
        rewrite: path => path,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Preserve original host for OAuth redirect URI detection
            const originalHost = req.headers.host;
            if (originalHost) {
              proxyReq.setHeader('X-Forwarded-Host', originalHost);
              proxyReq.setHeader('X-Forwarded-Proto', 'http');
            }
          });
        },
      },
    },
  },
  plugins: [
    tanstackRouter({
      tmpDir: '/tmp/tanstack-router',
      routeTreeFileDir: './src',
      routeTreeFileName: 'routeTree.gen.ts',
    }),
    react(),
    tailwindcss(),
    tsConfigPaths(),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
