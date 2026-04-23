<template>
  <div class="tx-icon" :class="catClass">{{ catEmoji }}</div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ category: String, size: { type: String, default: 'md' } })

const MAP = {
  'Food & Dining':    { cls: 'cat-food',     emoji: '🍽️' },
  'Rent & Housing':   { cls: 'cat-rent',     emoji: '🏠' },
  'Transportation':   { cls: 'cat-transit',  emoji: '🚌' },
  'Utilities':        { cls: 'cat-bills',    emoji: '🧾' },
  'Entertainment':    { cls: 'cat-fun',      emoji: '🎬' },
  'Health & Medical': { cls: 'cat-health',   emoji: '💊' },
  'Shopping':         { cls: 'cat-shopping', emoji: '🛍️' },
  'Travel':           { cls: 'cat-travel',   emoji: '✈️' },
  'Education':        { cls: 'cat-health',   emoji: '📚' },
  'Salary':           { cls: 'cat-salary',   emoji: '💼' },
  'Freelance':        { cls: 'cat-salary',   emoji: '💻' },
  'Other':            { cls: 'cat-other',    emoji: '📌' },
}
const entry = computed(() => MAP[props.category] || MAP['Other'])
const catClass = computed(() => entry.value.cls)
const catEmoji = computed(() => entry.value.emoji)
</script>
