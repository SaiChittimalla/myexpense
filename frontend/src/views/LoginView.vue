<template>
  <div class="login-screen">
    <div class="login-inner">
      <!-- Logo -->
      <div class="login-logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H21C22.1 20 23 19.1 23 18V6C23 4.9 22.1 4 21 4ZM21 18H3V12H21V18ZM21 8H3V6H21V8Z"/>
        </svg>
      </div>

      <!-- Heading -->
      <h1 class="login-heading">
        Welcome back,<br>
        <em class="display-italic">{{ greeting }}.</em>
      </h1>
      <p class="login-sub">Track spending, split bills with roommates, keep tabs on group trips.</p>

      <!-- Form -->
      <form @submit.prevent="doLogin">
        <div class="input-wrap">
          <label class="input-label">EMAIL</label>
          <div style="position:relative">
            <span class="input-icon">🏷️</span>
            <input v-model="email" class="input has-icon" type="email" placeholder="you@example.com" autocomplete="email" required />
          </div>
        </div>

        <div class="input-wrap">
          <label class="input-label">PASSWORD</label>
          <div style="position:relative">
            <span class="input-icon">🔑</span>
            <input v-model="password" class="input has-icon" :type="showPwd ? 'text' : 'password'" placeholder="••••••••" required />
            <button type="button" class="input-eye" @click="showPwd = !showPwd">{{ showPwd ? '🙈' : '👁️' }}</button>
          </div>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="btn btn-primary" :disabled="loading" style="margin-top:8px">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="login-footer">New here? <a href="/app/login" style="color:var(--accent);font-weight:700">Create account</a></p>

      <div class="login-divider"><span>or continue with</span></div>

      <div style="display:flex;justify-content:center">
        <button class="frappe-sso-btn" @click="ssoLogin">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="var(--accent)">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.18 5 4.05 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const showPwd = ref(false)
const loading = ref(false)
const error = ref('')
const greeting = ref('MyExpense')

async function doLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.message || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}

function ssoLogin() {
  window.location.href = '/app/login'
}
</script>

<style scoped>
.login-screen {
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  padding-top: calc(32px + var(--sat));
}
.login-inner { width: 100%; max-width: 360px; }
.login-logo {
  width: 52px; height: 52px; border-radius: 16px;
  background: var(--accent); display: flex; align-items: center; justify-content: center;
  margin-bottom: 28px;
}
.login-heading { font-size: 30px; line-height: 1.2; margin-bottom: 10px; }
.login-sub { color: var(--ink-muted); font-size: 14px; margin-bottom: 32px; line-height: 1.5; }
.login-footer { text-align: center; font-size: 14px; color: var(--ink-muted); margin-top: 20px; }
.login-divider {
  display: flex; align-items: center; gap: 12px; color: var(--ink-muted);
  font-size: 13px; margin: 24px 0 20px;
}
.login-divider::before, .login-divider::after { content: ''; flex: 1; height: 1px; background: rgba(42,36,28,.12); }
.frappe-sso-btn {
  width: 52px; height: 52px; border-radius: 50%; border: 1.5px solid rgba(42,36,28,.12);
  background: var(--white); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: box-shadow .15s;
}
.frappe-sso-btn:hover { box-shadow: 0 2px 8px rgba(42,36,28,.12); }
.error-msg { color: var(--expense); font-size: 13px; margin-bottom: 8px; padding: 10px 14px; background: #fde8e8; border-radius: 10px; }
</style>
