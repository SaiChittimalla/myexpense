import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getLoggedUser, login as frappeLogin, logout as frappeLogout } from '@/composables/useFrappe'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const isGuest = computed(() => !user.value || user.value === 'Guest')

  async function init() {
    try {
      const u = await getLoggedUser()
      user.value = (u && u !== 'Guest') ? u : null
    } catch {
      user.value = null
    }
  }

  async function login(email, password) {
    loading.value = true
    try {
      await frappeLogin(email, password)
      await init()
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await frappeLogout()
    user.value = null
  }

  return { user, loading, isGuest, init, login, logout }
})
