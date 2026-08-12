<script setup lang="ts">
withDefaults(defineProps<{ inverse?: boolean; compact?: boolean }>(), {
  inverse: false,
  compact: false,
})
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <span
      class="flex h-9 w-9 items-center justify-center rounded-lg"
      :class="inverse ? 'bg-white/10 text-white' : 'bg-[var(--ct-navy)] text-white'"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="h-5 w-5">
        <path d="M9 11l3 3L22 4" />
        <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
      </svg>
    </span>
    <span v-if="!compact" class="text-[17px] font-semibold tracking-[-0.025em]">
      Contably<span :class="inverse ? 'text-[var(--ct-accent)]' : 'text-[var(--ct-accent-ink)]'"
        >Task</span
      >
    </span>
  </span>
</template>
