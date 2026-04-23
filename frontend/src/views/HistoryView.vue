<template>
  <div class="screen">
    <div class="screen-content">

      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="display" style="font-size:32px">History</h1>
          <p class="caption" style="margin-top:2px">{{ store.historyTotal }} transactions · {{ monthLabel }}</p>
        </div>
        <button class="icon-btn-round">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
          </svg>
        </button>
      </div>

      <!-- Filter tabs -->
      <div class="filter-tabs">
        <button v-for="tab in tabs" :key="tab.key" class="filter-tab" :class="{ active: activeTab === tab.key }" @click="setTab(tab.key)">
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="store.loading" style="text-align:center;padding:40px 0;color:var(--ink-muted)">Loading…</div>

      <!-- Grouped records -->
      <template v-else>
        <template v-if="grouped.length">
          <template v-for="group in grouped" :key="group.date">
            <div class="date-label">{{ group.label }}</div>
            <div class="card" style="padding:4px 16px;margin-bottom:4px">
              <TransactionItem v-for="tx in group.items" :key="tx.name" :tx="tx" />
            </div>
          </template>
        </template>
        <div v-else class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>No {{ activeTab === 'all' ? '' : activeTab }} transactions found</p>
        </div>
      </template>

    </div>

    <AddExpenseModal v-if="showAdd" @close="showAdd = false" @saved="onSaved" />
    <BottomNav @add="showAdd = true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExpenseStore } from '@/stores/expense'
import BottomNav from '@/components/BottomNav.vue'
import TransactionItem from '@/components/TransactionItem.vue'
import AddExpenseModal from '@/components/AddExpenseModal.vue'

const store = useExpenseStore()
const showAdd = ref(false)
const activeTab = ref('all')

const tabs = [
  { key: 'all',     label: 'All' },
  { key: 'Expense', label: 'Expense' },
  { key: 'Income',  label: 'Income' },
  { key: 'split',   label: 'Split' },
]

const monthLabel = computed(() => new Date().toLocaleString('en-IN', { month: 'long' }))

const grouped = computed(() => {
  const recs = store.history
  const map = new Map()
  for (const tx of recs) {
    const key = tx.transaction_date
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(tx)
  }
  return [...map.entries()].map(([date, items]) => ({
    date,
    label: formatDateLabel(date),
    items,
  }))
})

function formatDateLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  const diff = Math.floor((now - d) / 86400000)
  if (diff === 0) return 'Yesterday'
  if (diff === 1) return 'Yesterday'
  return d.toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' }).toUpperCase()
}

async function setTab(tab) {
  activeTab.value = tab
  const filters = {}
  if (tab === 'Expense') filters.type_filter = 'Expense'
  else if (tab === 'Income') filters.type_filter = 'Income'
  else if (tab === 'split') filters.type_filter = 'Expense' // split expenses
  await store.fetchHistory(filters)
}

onMounted(() => store.fetchHistory())
async function onSaved() { showAdd.value = false; await store.fetchHistory() }
</script>

<style scoped>
.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 20px 0 16px;
}
.icon-btn-round {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  background: var(--surface); cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--ink); margin-top: 6px;
}
.filter-tabs {
  display: flex; gap: 0; margin-bottom: 20px;
  border-bottom: 1.5px solid rgba(42,36,28,.1);
}
.filter-tab {
  flex: 1; padding: 10px 0; border: none; background: none;
  font-size: 14px; font-weight: 600; color: var(--ink-muted); cursor: pointer;
  border-bottom: 2.5px solid transparent; margin-bottom: -1.5px; transition: all .15s;
}
.filter-tab.active { color: var(--ink); border-bottom-color: var(--accent); }
</style>
