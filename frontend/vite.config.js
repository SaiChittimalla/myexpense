import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

export default defineConfig(({ command }) => ({
  // dev: serve at '/', prod: assets load from Frappe's asset path
  base: command === 'build' ? '/assets/myexpense/myexpense/' : '/',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'logo.png'],
      manifest: {
        name: 'MyExpense',
        short_name: 'MyExpense',
        description: 'Personal & Group Expense Tracker',
        theme_color: '#d97757',
        background_color: '#faf6f0',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/app-mobile/',
        icons: [
          { src: 'logo-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'logo-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\//,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache', networkTimeoutSeconds: 10 }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') }
  },
  server: {
    port: 8080,
    host: '0.0.0.0',   // expose on local network so mobile can connect
    proxy: {
      '^/(api|app|assets|files|method|private|login|logout)': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        headers: { host: 'myexpense.local' }
      }
    }
  },
  build: {
    outDir: '../myexpense/public/myexpense',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  }
}))
