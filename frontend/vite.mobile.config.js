import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

// Server URL is now configured at runtime by the user in the app (stored in localStorage).
// No need to hardcode it here — the setup screen handles it on first launch.

export default defineConfig({
  base: '/',
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
