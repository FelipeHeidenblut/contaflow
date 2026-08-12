<script setup lang="ts">
import BaseModal from './BaseModal.vue'

withDefaults(
  defineProps<{
    open: boolean
    title: string
    message: string
    confirmLabel?: string
    busy?: boolean
  }>(),
  { confirmLabel: 'Confirmar', busy: false },
)

defineEmits<{ close: []; confirm: [] }>()
</script>

<template>
  <BaseModal
    :open="open"
    :title="title"
    :description="message"
    size="sm"
    :close-on-backdrop="!busy"
    @close="!busy && $emit('close')"
  >
    <div class="p-6 text-sm leading-relaxed text-slate-600">Esta ação não poderá ser desfeita.</div>
    <template #footer>
      <div class="flex justify-end gap-3">
        <button
          type="button"
          :disabled="busy"
          class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
          @click="$emit('close')"
        >
          Cancelar
        </button>
        <button
          type="button"
          :disabled="busy"
          class="rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:cursor-wait disabled:opacity-60"
          @click="$emit('confirm')"
        >
          {{ busy ? 'Processando...' : confirmLabel }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>
