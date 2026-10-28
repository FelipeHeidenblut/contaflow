<script setup lang="ts">
withDefaults(defineProps<{ inverse?: boolean; compact?: boolean }>(), {
  inverse: false,
  compact: false,
})
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <span
      class="flex h-7 w-7 items-center justify-center rounded-md"
      :class="inverse ? 'bg-white/10 text-white' : 'bg-[var(--ct-primary)] text-white shadow-sm'"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="h-5 w-5">
        <path d="m5 12 4 4L19 6" />
      </svg>
    </span>
    <span v-if="!compact" class="text-[21px] font-semibold tracking-[-0.025em]">
      Contably<span :class="inverse ? 'text-[var(--ct-accent)]' : 'text-[var(--ct-accent-ink)]'"
        >Task</span
      >
    </span>
  </span>
</template>
