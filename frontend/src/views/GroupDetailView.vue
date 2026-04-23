<template>
  <div class="screen">
    <div class="screen-content">

      <div class="page-header">
        <div style="display:flex;align-items:center;gap:12px">
          <RouterLink to="/groups" class="back-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
          </RouterLink>
          <div>
            <h1 class="display" style="font-size:26px">{{ detail?.group_name || id }}</h1>
            <p class="caption">{{ detail?.members?.length || 0 }} members</p>
          </div>
        </div>
      </div>

      <div v-if="loading" style="text-align:center;padding:60px 0;color:var(--ink-muted)">Loading…</div>

      <template v-else-if="detail">
        <!-- Total -->
        <div class="card" style="margin-bottom:16px">
          <p class="caption">TOTAL EXPENSES</p>
          <p style="font-size:32px;font-weight:700;margin-top:4px">₹{{ fmt(detail.total_expense) }}</p>
        </div>

        <!-- Members -->
        <h3 style="margin-bottom:12px;font-size:16px">Members</h3>
        <div class="card" style="padding:4px 16px;margin-bottom:20px">
          <div v-for="m in detail.members" :key="m.user" style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid rgba(42,36,28,.06)">
            <div class="avatar-sm" style="width:36px;height:36px;font-size:13px" :style="{ background: '#d97757' }">{{ initials(m) }}</div>
            <div style="flex:1">
              <div style="font-weight:600">{{ m.display_name || m.user }}</div>
              <div style="font-size:12px;color:var(--ink-muted)">{{ m.user }}</div>
            </div>
          </div>
        </div>

        <!-- Settlements -->
        <h3 style="margin-bottom:12px;font-size:16px">Settle up</h3>
        <div class="card" style="margin-bottom:20px">
          <p style="color:var(--ink-muted);font-size:14px;text-align:center;padding:16px 0">All settled up! 🎉</p>
        </div>
      </template>

    </div>

    <!-- Split expense modal -->
    <Teleport to="body" v-if="showSplit">
      <div class="modal-backdrop" @click.self="showSplit = false">
        <div class="modal-sheet">
          <div class="modal-header">
            <button class="modal-close" @click="showSplit = false">✕</button>
            <span class="modal-title">Split expense</span>
            <div style="width:32px" />
          </div>

          <!-- Total amount -->
          <div class="card-surface" style="margin-bottom:20px;text-align:center">
            <p class="caption">TOTAL · APRIL RENT</p>
            <p style="font-size:36px;font-weight:700;margin-top:6px">₹{{ fmt(splitAmount) }}<span style="font-size:18px;font-weight:600">.00</span></p>
          </div>

          <!-- Split type tabs -->
          <div style="display:flex;gap:8px;margin-bottom:20px">
            <button v-for="t in splitTypes" :key="t" class="split-type-btn" :class="{ active: splitType === t }" @click="splitType = t">{{ t }}</button>
          </div>

          <p class="caption" style="margin-bottom:12px">SPLIT BETWEEN</p>

          <!-- Members -->
          <div class="card" style="padding:4px 16px;margin-bottom:20px">
            <div v-for="m in splitMembers" :key="m.user" style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid rgba(42,36,28,.06)">
              <div class="avatar-sm" style="width:36px;height:36px;font-size:13px;background:#d97757">{{ m.init }}</div>
              <div style="flex:1">
                <div style="font-weight:600">{{ m.name }}</div>
                <div style="font-size:13px;color:var(--income)">₹{{ fmt(m.share) }}</div>
              </div>
              <input type="checkbox" :checked="m.included" @change="toggleMember(m)" style="width:20px;height:20px;accent-color:var(--accent)" />
            </div>
          </div>

          <!-- Summary -->
          <div style="background:#fde8d5;border-radius:12px;padding:14px;text-align:center;margin-bottom:20px">
            <p class="caption" style="color:var(--accent)">EACH PAYS</p>
            <p style="font-size:24px;font-weight:700;color:var(--accent)">₹{{ fmt(eachPays) }} ×{{ includedCount }}</p>
          </div>

          <button class="btn btn-primary" @click="confirmSplit">Confirm split</button>
        </div>
      </div>
    </Teleport>

    <AddExpenseModal v-if="showAdd" @close="showAdd = false" @saved="onSaved" />
    <BottomNav @add="showAdd = true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useFrappe } from '@/composables/useFrappe'
import { useExpenseStore } from '@/stores/expense'
import BottomNav from '@/components/BottomNav.vue'
import AddExpenseModal from '@/components/AddExpenseModal.vue'

const route = useRoute()
const { call } = useFrappe()
const store = useExpenseStore()
const id = computed(() => route.params.id)
const detail = ref(null)
const loading = ref(false)
const showAdd = ref(false)
const showSplit = ref(false)

const splitAmount = ref(12500)
const splitType = ref('Equal')
const splitTypes = ['Equal', 'Custom', 'Shares']
const splitMembers = ref([
  { user: 'r@x', init: 'R', name: 'Rohan · you', share: 4167, included: true },
  { user: 'a@x', init: 'A', name: 'Arjun', share: 4167, included: true },
  { user: 'd@x', init: 'D', name: 'Dev', share: 4167, included: true },
  { user: 'p@x', init: 'P', name: 'Priya', share: 0, included: false },
])
const includedCount = computed(() => splitMembers.value.filter(m => m.included).length)
const eachPays = computed(() => {
  const n = includedCount.value
  return n ? Math.round(splitAmount.value / n) : 0
})

function toggleMember(m) {
  m.included = !m.included
  recalcShares()
}
function recalcShares() {
  const n = includedCount.value
  const each = n ? Math.round(splitAmount.value / n) : 0
  splitMembers.value.forEach(m => { m.share = m.included ? each : 0 })
}

function fmt(n) { return Number(n || 0).toLocaleString('en-IN') }
function initials(m) { return (m.display_name || m.user || '').slice(0, 2).toUpperCase() }

async function confirmSplit() { showSplit.value = false }
async function onSaved() { showAdd.value = false }

onMounted(async () => {
  loading.value = true
  try { detail.value = await call('myexpense.api.group.get_group_detail', { group_name: id.value }) }
  catch { detail.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; padding: 20px 0 16px; }
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--surface);
  display: flex; align-items: center; justify-content: center; color: var(--ink); text-decoration: none;
}
.split-type-btn {
  flex: 1; padding: 10px 0; border-radius: 50px; border: none; font-size: 14px; font-weight: 600;
  background: var(--surface); color: var(--ink-muted); cursor: pointer; transition: all .15s;
}
.split-type-btn.active { background: var(--accent); color: #fff; }
</style>
