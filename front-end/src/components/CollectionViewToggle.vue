<script setup lang="ts">
withDefaults(defineProps<{ modelValue: 'cards' | 'lista'; cardsLabel?: string }>(), {
  cardsLabel: 'Cards',
})
const emit = defineEmits<{ 'update:modelValue': [value: 'cards' | 'lista'] }>()
</script>

<template>
  <div
    role="group"
    aria-label="Modo de visualização"
    class="inline-flex shrink-0 rounded-lg border border-[#e1e9f5] bg-white p-1"
  >
    <button
      v-for="option in [
        { value: 'cards', label: cardsLabel },
        { value: 'lista', label: 'Lista' },
      ] as const"
      :key="option.value"
      type="button"
      :aria-pressed="modelValue === option.value"
      class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors"
      :class="
        modelValue === option.value
          ? 'bg-blue-50 text-blue-600'
          : 'text-slate-500 hover:bg-slate-50'
      "
      @click="emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>
