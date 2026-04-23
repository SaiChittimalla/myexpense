import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useFrappe } from '@/composables/useFrappe'

const { call, get } = useFrappe()

export const useExpenseStore = defineStore('expense', () => {
  const dashboard = ref(null)
  const history = ref([])
  const historyTotal = ref(0)
  const groups = ref([])
  const reports = ref(null)
  const mode = ref('personal')        // 'personal' | 'group'
  const activeGroup = ref(null)
  const loading = ref(false)

  async function fetchDashboard() {
    loading.value = true
    try {
      dashboard.value = await call('myexpense.api.expense.get_dashboard', {
        mode: mode.value,
        group: activeGroup.value,
      })
    } finally { loading.value = false }
  }

  async function fetchHistory(filters = {}) {
    loading.value = true
    try {
      const res = await call('myexpense.api.expense.get_history', {
        mode: mode.value,
        group: activeGroup.value,
        ...filters,
      })
      history.value = res.records
      historyTotal.value = res.total
    } finally { loading.value = false }
  }

  async function addExpense(payload) {
    const res = await call('myexpense.api.expense.add_expense', payload)
    await fetchDashboard()
    return res
  }

  async function deleteExpense(name) {
    await call('myexpense.api.expense.delete_expense', { name })
    await fetchHistory()
  }

  async function fetchGroups() {
    groups.value = await call('myexpense.api.group.get_groups')
  }

  async function fetchReports(params = {}) {
    reports.value = await call('myexpense.api.expense.get_reports', {
      mode: mode.value,
      group: activeGroup.value,
      ...params,
    })
  }

  function setMode(m, group = null) {
    mode.value = m
    activeGroup.value = group
  }

  return {
    dashboard, history, historyTotal, groups, reports,
    mode, activeGroup, loading,
    fetchDashboard, fetchHistory, addExpense, deleteExpense,
    fetchGroups, fetchReports, setMode,
  }
})
