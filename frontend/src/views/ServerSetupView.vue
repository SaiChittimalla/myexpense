<template>
  <div class="setup-screen">
    <div class="setup-card">
      <div class="setup-logo">💸</div>
      <h1 class="setup-title">MyExpense</h1>
      <p class="setup-sub">Enter your server address to get started</p>

      <label class="caption input-label">SERVER URL</label>
      <input
        v-model="url"
        class="input"
        type="url"
        inputmode="url"
        placeholder="http://192.168.1.107:8000"
        autocapitalize="none"
        autocorrect="off"
        spellcheck="false"
        @keyup.enter="save"
      />
      <p class="setup-hint">Your local IP on WiFi, e.g. <code>http://192.168.x.x:8000</code></p>

      <div v-if="error" class="setup-error">{{ error }}</div>

      <button class="btn btn-primary" style="margin-top:8px" :disabled="!url || checking" @click="save">
        {{ checking ? 'Checking…' : 'Connect' }}
      </button>

      <p class="setup-hint" style="margin-top:16px">
        Find your IP: open a terminal on your PC and run <code>hostname -I</code>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { setServerUrl } from '@/composables/useFrappe'

const router = useRouter()
const url = ref('')
const checking = ref(false)
const error = ref('')

async function save() {
  if (!url.value.trim()) return
  error.value = ''
  checking.value = true
  try {
    const cleaned = url.value.trim().replace(/\/$/, '')
    // Quick connectivity check
    const res = await fetch(`${cleaned}/api/method/myexpense.api.auth.get_session_user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    })
    if (!res.ok && res.status !== 403 && res.status !== 401) {
      throw new Error(`Server responded with ${res.status}`)
    }
    setServerUrl(cleaned)
    router.replace('/login')
  } catch (e) {
    error.value = 'Could not reach server. Check the URL and make sure you are on the same WiFi.'
  } finally {
    checking.value = false
  }
}
</script>

<style scoped>
.setup-screen {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 24px;
}
.setup-card {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.setup-logo {
  font-size: 56px;
  text-align: center;
  margin-bottom: 8px;
}
.setup-title {
  font-size: 28px;
  font-weight: 800;
  text-align: center;
  margin: 0 0 4px;
}
.setup-sub {
  font-size: 15px;
  color: var(--ink-muted);
  text-align: center;
  margin: 0 0 24px;
}
.setup-hint {
  font-size: 12px;
  color: var(--ink-muted);
  margin: 6px 0 0;
}
.setup-hint code {
  background: var(--surface);
  padding: 1px 4px;
  border-radius: 4px;
  font-size: 11px;
}
.setup-error {
  background: #fdecea;
  color: var(--expense);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  margin-top: 8px;
}
</style>
