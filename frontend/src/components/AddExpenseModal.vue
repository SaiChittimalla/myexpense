<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-sheet">
        <div class="modal-header">
          <button class="modal-close" @click="$emit('close')">✕</button>
          <span class="modal-title">New transaction</span>
          <div style="width:32px" />
        </div>

        <!-- Type toggle -->
        <div class="type-toggle" style="margin-bottom:24px">
          <button :class="{ 'active-expense': form.type === 'Expense' }" @click="form.type = 'Expense'">Expense</button>
          <button :class="{ 'active-income': form.type === 'Income' }" @click="form.type = 'Income'">Income</button>
        </div>

        <!-- Amount -->
        <div style="text-align:center; margin-bottom:24px">
          <label class="caption" style="display:block;margin-bottom:8px">AMOUNT</label>
          <div class="amount-display" @click="focusAmount">
            <span class="symbol">₹</span>
            <input
              ref="amountRef"
              v-model="form.amount"
              type="number"
              inputmode="decimal"
              placeholder="0"
              style="border:none;background:none;font-size:52px;font-weight:700;width:140px;text-align:center;outline:none;color:var(--ink)"
            />
          </div>
          <div style="height:2px;width:80px;background:var(--accent);margin:8px auto 0" />
        </div>

        <!-- Category grid -->
        <label class="caption" style="display:block;margin-bottom:10px">CATEGORY</label>
        <div class="cat-grid">
          <button
            v-for="cat in categories" :key="cat.key"
            class="cat-btn" :class="{ selected: form.category === cat.label }"
            @click="form.category = cat.label"
          >
            <div class="cat-icon-wrap" :class="cat.cls">{{ cat.emoji }}</div>
            <span>{{ cat.short }}</span>
          </button>
        </div>

        <!-- Note -->
        <label class="caption input-label">NOTE</label>
        <input v-model="form.notes" class="input" type="text" placeholder="What's this for?" style="margin-bottom:16px" />

        <!-- Date + Group mode row -->
        <div style="display:flex;gap:10px;margin-bottom:24px">
          <button class="btn btn-outline btn-sm" style="flex:1;gap:6px" @click="showDatePicker = true">
            📅 {{ form.transaction_date || 'Today' }}
          </button>
          <button class="btn btn-outline btn-sm" style="flex:1;gap:6px" @click="showSplitOptions = !showSplitOptions">
            👥 {{ form.is_group_expense ? 'Group' : 'Personal' }}
          </button>
        </div>

        <!-- Group / split options -->
        <template v-if="showSplitOptions">
          <div class="card-surface" style="margin-bottom:16px">
            <label class="caption input-label">GROUP</label>
            <select v-model="form.group" class="input" style="margin-bottom:8px" @change="form.is_group_expense = !!form.group">
              <option value="">Personal (no group)</option>
              <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.group_name }}</option>
            </select>
            <template v-if="form.group">
              <label style="display:flex;align-items:center;gap:8px;font-size:14px;cursor:pointer">
                <input type="checkbox" v-model="form.is_split" /> Split this expense
              </label>
            </template>
          </div>
        </template>

        <!-- Submit -->
        <button
          class="btn" :class="form.type === 'Income' ? 'btn-income' : 'btn-primary'"
          :disabled="!form.amount || saving"
          @click="submit"
        >
          {{ saving ? 'Saving…' : (form.type === 'Income' ? 'Add income' : 'Add expense') }}
        </button>

        <div style="height:8px" />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useExpenseStore } from '@/stores/expense'

const emit = defineEmits(['close', 'saved'])
const store = useExpenseStore()
const saving = ref(false)
const showSplitOptions = ref(false)
const showDatePicker = ref(false)
const amountRef = ref(null)
const groups = ref([])

const form = reactive({
  title: '', amount: '', type: 'Expense', category: 'Food & Dining',
  transaction_date: new Date().toISOString().slice(0, 10),
  notes: '', is_group_expense: 0, group: '', is_split: 0,
})

const categories = [
  { key: 'food',     label: 'Food & Dining',    short: 'Food',    cls: 'cat-food',     emoji: '🍽️' },
  { key: 'rent',     label: 'Rent & Housing',   short: 'Rent',    cls: 'cat-rent',     emoji: '🏠' },
  { key: 'transit',  label: 'Transportation',   short: 'Transit', cls: 'cat-transit',  emoji: '🚌' },
  { key: 'shopping', label: 'Shopping',         short: 'Shopping',cls: 'cat-shopping', emoji: '🛍️' },
  { key: 'bills',    label: 'Utilities',        short: 'Bills',   cls: 'cat-bills',    emoji: '🧾' },
  { key: 'fun',      label: 'Entertainment',    short: 'Fun',     cls: 'cat-fun',      emoji: '🎬' },
  { key: 'health',   label: 'Health & Medical', short: 'Health',  cls: 'cat-health',   emoji: '💊' },
  { key: 'salary',   label: 'Salary',           short: 'Salary',  cls: 'cat-salary',   emoji: '💼' },
]

onMounted(async () => {
  await store.fetchGroups()
  groups.value = store.groups
  setTimeout(() => amountRef.value?.focus(), 300)
})

function focusAmount() { amountRef.value?.focus() }

async function submit() {
  if (!form.amount) return
  saving.value = true
  try {
    const payload = {
      title: form.notes || form.category,
      amount: form.amount,
      type: form.type,
      category: form.category,
      transaction_date: form.transaction_date,
      notes: form.notes,
      is_group_expense: form.group ? 1 : 0,
      group: form.group || null,
      is_split: form.is_split ? 1 : 0,
    }
    await store.addExpense(payload)
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
