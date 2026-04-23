import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

// ── Change this to your deployed server URL ──────────────────────────────────
// For local network testing:  http://192.168.1.107:8000
// For production server:       https://myexpense.yourdomain.com
const API_BASE = 'http://192.168.1.107:8000'
// ─────────────────────────────────────────────────────────────────────────────

export default defineConfig({
  base: '/',
  define: {
    '__API_BASE__': JSON.stringify(API_BASE),
  },
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'MyExpense',
        short_name: 'MyExpense',
        description: 'Personal & Group Expense Tracker',
        theme_color: '#d97757',
        background_color: '#faf6f0',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: 'logo-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'logo-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
    })
  ],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
})
