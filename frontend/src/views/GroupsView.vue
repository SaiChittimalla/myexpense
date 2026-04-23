<template>
  <div class="screen">
    <div class="screen-content">

      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="display" style="font-size:32px">Groups</h1>
          <p class="caption" style="margin-top:2px">{{ groups.length }} shared · ₹{{ fmt(Math.abs(netBalance)) }} net</p>
        </div>
        <button class="add-btn" @click="showCreate = true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      </div>

      <!-- Net balance card -->
      <div class="net-card" v-if="groups.length">
        <div class="net-label">{{ netBalance >= 0 ? "YOU'RE OWED" : 'YOU OWE' }}</div>
        <div class="net-amount positive">₹{{ fmt(Math.abs(netBalance)) }}<span style="font-size:18px;font-weight:600">.00</span></div>
        <div class="net-bar">
          <div class="net-bar-fill" :style="{ width: barWidth + '%' }" />
        </div>
        <div class="net-bar-labels">
          <span>Owed ₹{{ fmt(totalOwed) }}</span>
          <span>Owe ₹{{ fmt(totalOwe) }}</span>
        </div>
      </div>

      <!-- Group cards -->
      <div v-if="store.loading" style="text-align:center;padding:40px 0;color:var(--ink-muted)">Loading…</div>
      <template v-else>
        <RouterLink
          v-for="g in groups" :key="g.name"
          :to="`/groups/${g.name}`"
          class="group-card-link"
        >
          <div class="group-card">
            <div class="group-icon" :style="{ background: groupColor(g.name) }">{{ groupEmoji(g.group_name) }}</div>
            <div class="group-body">
              <div class="group-name">{{ g.group_name }}</div>
              <div class="group-sub">{{ g.member_count || '—' }} members · {{ memberNames(g) }}</div>
              <div class="group-avatars" style="margin-top:8px">
                <div v-for="(init, i) in memberInitials(g)" :key="i" class="avatar-sm" :style="{ background: avatarColor(i) }">{{ init }}</div>
              </div>
            </div>
            <div class="group-right">
              <div>
                <div class="owed-label" :class="groupBalance(g) >= 0 ? 'owed' : 'owe'">{{ groupBalance(g) >= 0 ? 'OWED' : 'OWE' }}</div>
                <div class="owed-amount" :class="groupBalance(g) >= 0 ? 'owed' : 'owe'">₹{{ fmt(Math.abs(groupBalance(g))) }}</div>
              </div>
              <button class="btn-settle" @click.prevent="settle(g)">Settle up ›</button>
            </div>
          </div>
        </RouterLink>

        <div v-if="!groups.length" class="empty-state">
          <div class="empty-icon">👥</div>
          <p>No groups yet. Create one to split expenses!</p>
        </div>
      </template>

    </div>

    <!-- Create group modal -->
    <Teleport to="body" v-if="showCreate">
      <div class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal-sheet">
          <div class="modal-header">
            <button class="modal-close" @click="showCreate = false">✕</button>
            <span class="modal-title">New Group</span>
            <div style="width:32px" />
          </div>
          <label class="input-label">GROUP NAME</label>
          <input v-model="newGroup.name" class="input" placeholder="e.g. Flat 4B, Goa Trip" style="margin-bottom:16px" />
          <label class="input-label">DESCRIPTION</label>
          <input v-model="newGroup.description" class="input" placeholder="Optional" style="margin-bottom:24px" />
          <button class="btn btn-primary" :disabled="!newGroup.name || creating" @click="createGroup">
            {{ creating ? 'Creating…' : 'Create group' }}
          </button>
        </div>
      </div>
    </Teleport>

    <AddExpenseModal v-if="showAdd" @close="showAdd = false" @saved="onSaved" />
    <BottomNav @add="showAdd = true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { RouterLink } from 'vue-router'
import { useExpenseStore } from '@/stores/expense'
import { useFrappe } from '@/composables/useFrappe'
import BottomNav from '@/components/BottomNav.vue'
import AddExpenseModal from '@/components/AddExpenseModal.vue'

const store = useExpenseStore()
const { call } = useFrappe()
const showAdd = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const newGroup = reactive({ name: '', description: '' })

const groups = computed(() => store.groups)

const netBalance = computed(() => 0)
const totalOwed = computed(() => 4400)
const totalOwe = computed(() => 1840)
const barWidth = computed(() => {
  const total = totalOwed.value + totalOwe.value
  return total ? (totalOwed.value / total) * 100 : 50
})

function fmt(n) { return Number(n || 0).toLocaleString('en-IN') }
function groupBalance(g) { return g.balance || 0 }
function memberNames(g) { return (g.owner_user || '').split('@')[0] }
function memberInitials(g) { return ['R', 'A', 'D'].slice(0, 3) }

const COLORS = ['#d97757', '#4a8c6a', '#5b7ec8', '#c85c5c', '#a87820']
function groupColor(name) {
  const i = name.charCodeAt(0) % COLORS.length
  return COLORS[i] + '22'
}
function avatarColor(i) { return COLORS[i % COLORS.length] }

const GROUP_EMOJIS = { flat: '🏠', goa: '🌴', office: '🍽️', trip: '✈️', room: '🏠' }
function groupEmoji(name) {
  const lower = name.toLowerCase()
  for (const [k, v] of Object.entries(GROUP_EMOJIS)) {
    if (lower.includes(k)) return v
  }
  return '👥'
}

function settle(g) { /* open settle modal */ }

async function createGroup() {
  creating.value = true
  try {
    await call('myexpense.api.group.create_group', { group_name: newGroup.name, description: newGroup.description })
    showCreate.value = false
    newGroup.name = ''
    newGroup.description = ''
    await store.fetchGroups()
  } finally { creating.value = false }
}

onMounted(() => store.fetchGroups())
async function onSaved() { showAdd.value = false }
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 20px 0 16px; }
.add-btn {
  width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid var(--ink);
  background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; margin-top: 6px;
}
.group-card-link { text-decoration: none; color: inherit; display: block; }
</style>
