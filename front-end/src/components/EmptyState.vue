<script setup lang="ts">
defineProps<{ title: string; description: string; actionLabel?: string }>()
defineEmits<{ action: [] }>()
</script>

<template>
  <div class="px-6 py-14 text-center">
    <div
      class="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]"
    >
      <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.8"
          d="M9 12h6m-3-3v6m9-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </div>
    <p class="mt-4 text-sm font-semibold text-[var(--ct-ink)]">{{ title }}</p>
    <p class="mx-auto mt-1 max-w-md text-sm text-[var(--ct-text-muted)]">{{ description }}</p>
    <button
      v-if="actionLabel"
      type="button"
      class="mt-5 rounded-lg bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[var(--ct-primary-hover)]"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>
