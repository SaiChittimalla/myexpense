<template>
  <div class="screen">
    <div class="screen-content">

      <!-- Header -->
      <div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0 16px">
        <RouterLink to="/" class="back-btn">✕</RouterLink>
        <span style="font-size:17px;font-weight:700">Profile</span>
        <button class="icon-btn-round" style="font-size:16px">⚙️</button>
      </div>

      <!-- Avatar -->
      <div style="text-align:center;margin-bottom:16px">
        <div class="profile-avatar" style="background:#b8a8e8;margin:0 auto 8px">
          {{ initials }}
          <div class="avatar-edit">+</div>
        </div>
        <h2 style="font-size:20px;font-weight:700">{{ profile.full_name || auth.user }}</h2>
        <p class="muted" style="font-size:14px">{{ auth.user }}</p>
      </div>

      <!-- Stats -->
      <div class="profile-stats">
        <div class="profile-stat">
          <div class="profile-stat-val">{{ stats.transactions }}</div>
          <div class="profile-stat-lbl">Transactions</div>
        </div>
        <div class="profile-stat">
          <div class="profile-stat-val">{{ stats.groups }}</div>
          <div class="profile-stat-lbl">Groups</div>
        </div>
        <div class="profile-stat">
          <div class="profile-stat-val">{{ stats.streak }}d</div>
          <div class="profile-stat-lbl">Streak</div>
        </div>
      </div>

      <!-- Account section -->
      <p class="caption" style="margin:20px 0 8px">ACCOUNT</p>
      <div class="settings-group">
        <div class="settings-row">
          <div class="settings-icon">🏷️</div>
          <div class="settings-body"><div class="settings-title">Email</div><div class="settings-sub">{{ auth.user }}</div></div>
          <span class="settings-arrow">›</span>
        </div>
        <div class="settings-row">
          <div class="settings-icon">🔑</div>
          <div class="settings-body"><div class="settings-title">Security</div><div class="settings-sub">Face ID · 6-digit PIN</div></div>
          <span class="settings-arrow">›</span>
        </div>
        <div class="settings-row">
          <div class="settings-icon">🏦</div>
          <div class="settings-body"><div class="settings-title">Linked accounts</div><div class="settings-sub">2 banks · UPI</div></div>
          <span class="settings-arrow">›</span>
        </div>
      </div>

      <!-- Preferences -->
      <p class="caption" style="margin:20px 0 8px">PREFERENCES</p>
      <div class="settings-group">
        <div class="settings-row">
          <div class="settings-icon">💱</div>
          <div class="settings-body"><div class="settings-title">Currency</div><div class="settings-sub">₹</div></div>
          <span class="settings-arrow">›</span>
        </div>
        <div class="settings-row">
          <div class="settings-icon">🔔</div>
          <div class="settings-body"><div class="settings-title">Notifications</div><div class="settings-sub">Daily summary</div></div>
          <span class="settings-arrow">›</span>
        </div>
        <div class="settings-row">
          <div class="settings-icon">☀️</div>
          <div class="settings-body"><div class="settings-title">Appearance</div><div class="settings-sub">Light</div></div>
          <span class="settings-arrow">›</span>
        </div>
      </div>

      <!-- Data -->
      <p class="caption" style="margin:20px 0 8px">DATA</p>
      <div class="settings-group">
        <div class="settings-row" @click="exportData">
          <div class="settings-icon">📅</div>
          <div class="settings-body"><div class="settings-title">Export data</div><div class="settings-sub">CSV · PDF</div></div>
          <span class="settings-arrow">›</span>
        </div>
        <div class="settings-row">
          <div class="settings-icon">👥</div>
          <div class="settings-body"><div class="settings-title">Manage roommates</div><div class="settings-sub">{{ stats.groups * 3 }} people</div></div>
          <span class="settings-arrow">›</span>
        </div>
      </div>

      <!-- Sign out -->
      <button class="btn btn-outline" style="margin-top:24px;color:var(--expense);border-color:var(--expense)" @click="doLogout">
        Sign out
      </button>
      <p style="text-align:center;font-size:12px;color:var(--ink-muted);margin-top:20px">MyExpense · v1.0.0</p>

      <div style="height:24px" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFrappe } from '@/composables/useFrappe'

const auth = useAuthStore()
const router = useRouter()
const { call } = useFrappe()

const profile = ref({ full_name: '' })
const stats = ref({ transactions: 10, groups: 3, streak: 12 })

const initials = computed(() => {
  const n = profile.value.full_name || auth.user || ''
  return n.slice(0, 2).toUpperCase()
})

async function doLogout() {
  await auth.logout()
  router.push('/login')
}

async function exportData() {
  try {
    const res = await call('myexpense.api.group.export_data')
    const blob = new Blob([res.csv], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'myexpense_data.csv'
    a.click()
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  try {
    const p = await call('myexpense.api.group.get_profile')
    profile.value = p
  } catch {}
})
</script>

<style scoped>
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--surface);
  display: flex; align-items: center; justify-content: center; font-size: 16px;
  text-decoration: none; color: var(--ink); border: none; cursor: pointer;
}
.icon-btn-round {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  background: var(--surface); cursor: pointer; display: flex; align-items: center; justify-content: center;
}
</style>
