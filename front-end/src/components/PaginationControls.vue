<script setup lang="ts">
defineProps<{
  page: number
  pages: number
  total: number
}>()

const emit = defineEmits<{
  change: [page: number]
}>()
</script>

<template>
  <nav
    v-if="pages > 1"
    class="flex flex-col gap-3 border-t border-[var(--ct-border)] px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
    aria-label="Paginação"
  >
    <p class="text-xs text-[var(--ct-text-muted)]">
      Página {{ page }} de {{ pages }} · {{ total }} resultados
    </p>
    <div class="flex items-center gap-2">
      <button
        type="button"
        class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2 text-sm font-medium text-[var(--ct-ink)] disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="page <= 1"
        aria-label="Ir para a página anterior"
        @click="emit('change', page - 1)"
      >
        Anterior
      </button>
      <button
        type="button"
        class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2 text-sm font-medium text-[var(--ct-ink)] disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="page >= pages"
        aria-label="Ir para a próxima página"
        @click="emit('change', page + 1)"
      >
        Próxima
      </button>
    </div>
  </nav>
</template>
