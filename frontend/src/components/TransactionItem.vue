<template>
  <div class="tx-item fade-in">
    <CategoryIcon :category="tx.category" />
    <div class="tx-body">
      <div class="tx-title">{{ tx.title }}</div>
      <div class="tx-sub">{{ tx.category || 'Other' }}<template v-if="tx.notes"> · {{ tx.notes }}</template></div>
    </div>
    <div class="tx-amount" :class="tx.type === 'Income' ? 'pos' : 'neg'">
      {{ tx.type === 'Income' ? '+' : '-' }}₹{{ fmt(tx.amount) }}
    </div>
  </div>
</template>

<script setup>
import CategoryIcon from './CategoryIcon.vue'
defineProps({ tx: Object })
function fmt(n) { return Number(n).toLocaleString('en-IN') }
</script>
