<template>
  <div class="screen">
    <div class="screen-content">

      <!-- Header -->
      <div class="home-header">
        <div>
          <h2 class="home-greeting display">Hello, <em>{{ firstName }}</em></h2>
          <p class="caption">{{ todayLabel }}</p>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <button class="icon-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </button>
          <button class="icon-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </button>
          <RouterLink to="/profile" class="avatar-btn">{{ initials }}</RouterLink>
        </div>
      </div>

      <!-- Loading -->
      <template v-if="store.loading && !dash">
        <div style="text-align:center;padding:60px 0;color:var(--ink-muted)">Loading…</div>
      </template>

      <template v-else-if="dash">
        <!-- Balance card -->
        <div class="card" style="margin-bottom:16px">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
            <span class="caption">BALANCE · {{ monthLabel }}</span>
            <button class="icon-btn" style="font-size:14px">ℹ️</button>
          </div>
          <div class="balance-amount display">₹{{ fmt(Math.abs(dash.balance)) }}<span class="balance-paise">.00</span></div>

          <div class="stats-row" style="margin-top:14px">
            <div class="stat-card" style="background:#e8f5ed">
              <div class="stat-label" style="color:var(--income)">↓ INCOME</div>
              <div class="stat-value" style="color:var(--income)">₹{{ fmt(dash.total_income) }}</div>
            </div>
            <div class="stat-card" style="background:#fde8e8">
              <div class="stat-label" style="color:var(--expense)">↑ SPENT</div>
              <div class="stat-value" style="color:var(--expense)">₹{{ fmt(dash.total_expense) }}</div>
            </div>
          </div>
        </div>

        <!-- Spending trend -->
        <div class="card" style="margin-bottom:16px">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div>
              <p class="caption">LAST 6 MONTHS</p>
              <h3 style="font-size:16px;margin-top:2px">Spending trend</h3>
            </div>
            <span class="badge-sm badge-down" v-if="trendPct">{{ trendPct }}%</span>
          </div>
          <div class="bar-chart">
            <div class="bar-wrap" v-for="(bar, i) in trendBars" :key="i">
              <div class="bar" :class="{ current: i === trendBars.length - 1 }" :style="{ height: bar.h + 'px' }" />
              <span class="bar-month">{{ bar.label }}</span>
            </div>
          </div>
        </div>

        <!-- Recent transactions -->
        <div class="section-header">
          <h3>Recent</h3>
          <RouterLink to="/history" class="see-all">See all</RouterLink>
        </div>
        <div class="card" style="padding:4px 16px">
          <template v-if="dash.recent_transactions?.length">
            <TransactionItem v-for="tx in dash.recent_transactions" :key="tx.name" :tx="tx" />
          </template>
          <div v-else class="empty-state"><div class="empty-icon">💸</div><p>No transactions yet</p></div>
        </div>

        <!-- You're owed -->
        <template v-if="dash.mode === 'group' && dash.balances?.length">
          <div class="section-header" style="margin-top:20px">
            <h3>You're owed</h3>
            <span class="badge-sm badge-down">₹{{ fmt(owedTotal) }}</span>
          </div>
          <div class="card-surface" style="display:flex;flex-wrap:wrap;gap:8px;padding:14px">
            <template v-for="b in dash.balances" :key="b.user">
              <span v-if="b.balance > 0" class="pill pill-income">{{ shortName(b.user) }} · ₹{{ fmt(b.balance) }}</span>
            </template>
          </div>
        </template>

        <div style="height:24px" />
      </template>

    </div>

    <AddExpenseModal v-if="showAdd" @close="showAdd = false" @saved="onSaved" />
    <BottomNav @add="showAdd = true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useExpenseStore } from '@/stores/expense'
import BottomNav from '@/components/BottomNav.vue'
import TransactionItem from '@/components/TransactionItem.vue'
import AddExpenseModal from '@/components/AddExpenseModal.vue'

const auth = useAuthStore()
const store = useExpenseStore()
const showAdd = ref(false)
const dash = computed(() => store.dashboard)

const firstName = computed(() => {
  const u = auth.user || ''
  return u.includes('@') ? u.split('@')[0] : u.split(' ')[0]
})
const initials = computed(() => firstName.value.slice(0, 2).toUpperCase())

const todayLabel = computed(() => new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' }))
const monthLabel = computed(() => new Date().toLocaleString('en-IN', { month: 'long' }).toUpperCase())

function fmt(n) { return Number(n || 0).toLocaleString('en-IN') }
function shortName(u) { return u.split('@')[0].split(' ')[0] }

const owedTotal = computed(() => {
  if (!dash.value?.balances) return 0
  return dash.value.balances.filter(b => b.balance > 0).reduce((s, b) => s + b.balance, 0)
})

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const trendBars = computed(() => {
  const now = new Date()
  const bars = []
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    bars.push({ label: MONTHS[d.getMonth()], h: 20 + Math.random() * 40 })
  }
  if (bars.length) bars[bars.length - 1].h = 60
  return bars
})

const trendPct = ref('-7.5')

onMounted(() => store.fetchDashboard())
async function onSaved() { showAdd.value = false; await store.fetchDashboard() }
</script>

<style scoped>
.home-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 0 16px;
}
.home-greeting { font-size: 24px; }
.icon-btn {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--ink);
}
.avatar-btn {
  width: 36px; height: 36px; border-radius: 50%; background: #b8a8e8;
  color: #fff; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center;
  text-decoration: none;
}
.balance-amount { font-size: 40px; font-weight: 700; }
.balance-paise  { font-size: 18px; font-weight: 600; color: var(--ink-muted); }
</style>
