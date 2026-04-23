<template>
  <div class="screen">
    <div class="screen-content">

      <div class="page-header">
        <div>
          <h1 class="display" style="font-size:32px">Reports</h1>
          <p class="caption">Category breakdown</p>
        </div>
        <button class="icon-btn-round">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="12" y1="18" x2="20" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Month tabs -->
      <div class="month-tabs">
        <button v-for="m in months" :key="m.key" class="month-tab" :class="{ active: activeMonth === m.key }" @click="setMonth(m.key)">
          {{ m.label }}
        </button>
      </div>

      <!-- Donut chart -->
      <div class="card" style="margin-bottom:16px;padding:20px">
        <div class="donut-wrap">
          <canvas ref="chartRef" width="200" height="200" />
          <div class="donut-center">
            <span class="dc-label">SPENT</span>
            <span class="dc-amount">₹{{ fmt(totalSpent) }}</span>
            <span class="dc-sub">{{ activeMonthLabel }} 2026</span>
          </div>
        </div>
      </div>

      <!-- Category legend -->
      <div class="card" style="margin-bottom:16px;padding:4px 16px">
        <div v-for="(cat, i) in catBreakdown" :key="cat.name" class="cat-legend-row">
          <div class="cat-dot" :style="{ background: chartColors[i % chartColors.length] }" />
          <span class="cat-legend-name">{{ cat.category || 'Other' }}</span>
          <span class="cat-legend-amount">₹{{ fmt(cat.total) }}</span>
          <span class="cat-legend-pct">{{ pct(cat.total) }}%</span>
        </div>
        <div v-if="!catBreakdown.length" class="empty-state"><p>No data for this month</p></div>
      </div>

      <!-- Weekly pace -->
      <h3 style="margin-bottom:12px;font-size:16px">Weekly pace</h3>
      <div class="card" style="padding:20px 16px">
        <div class="bar-chart">
          <div class="bar-wrap" v-for="(w, i) in weeklyBars" :key="i">
            <div class="bar" :class="{ current: i === 1 }" :style="{ height: w.h + 'px' }" />
            <span class="bar-month">{{ w.label }}</span>
          </div>
        </div>
      </div>

      <div style="height:24px" />
    </div>

    <AddExpenseModal v-if="showAdd" @close="showAdd = false" @saved="onSaved" />
    <BottomNav @add="showAdd = true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js'
import { useExpenseStore } from '@/stores/expense'
import BottomNav from '@/components/BottomNav.vue'
import AddExpenseModal from '@/components/AddExpenseModal.vue'

Chart.register(DoughnutController, ArcElement, Tooltip, Legend)

const store = useExpenseStore()
const showAdd = ref(false)
const chartRef = ref(null)
let chartInstance = null

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const now = new Date()
const months = MONTHS.map((label, i) => ({ key: i + 1, label })).filter((_, i) => {
  const diff = (now.getMonth()) - i
  return diff >= 0 && diff < 6
}).reverse()

const activeMonth = ref(now.getMonth() + 1)
const activeMonthLabel = computed(() => MONTHS[activeMonth.value - 1])

const chartColors = ['#5b8dd4', '#d97757', '#a87820', '#4ab8a0', '#c050a0', '#c85c5c']

const catBreakdown = computed(() => store.reports?.by_category || [
  { category: 'Rent & Housing', total: 12500 },
  { category: 'Food & Dining',  total: 4800 },
  { category: 'Utilities',      total: 1199 },
  { category: 'Transportation', total: 1800 },
  { category: 'Shopping',       total: 3200 },
  { category: 'Entertainment',  total: 1499 },
])

const totalSpent = computed(() => catBreakdown.value.reduce((s, c) => s + (c.total || 0), 0))
function fmt(n) { return Number(n || 0).toLocaleString('en-IN') }
function pct(v) { return totalSpent.value ? Math.round((v / totalSpent.value) * 100) : 0 }

const weeklyBars = [
  { label: 'W1', h: 30 }, { label: 'W2', h: 60 }, { label: 'W3', h: 25 }, { label: 'W4', h: 15 },
]

function buildChart() {
  if (!chartRef.value) return
  if (chartInstance) { chartInstance.destroy() }
  chartInstance = new Chart(chartRef.value, {
    type: 'doughnut',
    data: {
      labels: catBreakdown.value.map(c => c.category || 'Other'),
      datasets: [{
        data: catBreakdown.value.map(c => c.total),
        backgroundColor: chartColors,
        borderWidth: 0,
        spacing: 2,
        borderRadius: 4,
      }],
    },
    options: {
      cutout: '72%',
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      animation: { duration: 600 },
    },
  })
}

async function setMonth(m) {
  activeMonth.value = m
  await store.fetchReports()
  await nextTick()
  buildChart()
}

onMounted(async () => {
  await store.fetchReports()
  await nextTick()
  buildChart()
})

async function onSaved() { showAdd.value = false; await store.fetchReports(); buildChart() }
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 20px 0 16px; }
.icon-btn-round {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  background: var(--surface); cursor: pointer; display: flex; align-items: center; justify-content: center; margin-top: 6px;
}
</style>
