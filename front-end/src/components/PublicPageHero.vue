<script setup lang="ts">
withDefaults(
  defineProps<{ eyebrow: string; title: string; description: string; alignStart?: boolean }>(),
  { alignStart: false },
)
</script>

<template>
  <section class="ct-public-hero">
    <div
      class="ct-container"
      :class="
        $slots.default
          ? ['ct-public-hero-grid', { 'ct-public-hero-start': alignStart }]
          : 'ct-public-hero-centered'
      "
    >
      <div>
        <p class="ct-public-eyebrow">{{ eyebrow }}</p>
        <h1 class="ct-public-title">{{ title }}</h1>
        <p class="ct-public-lead">{{ description }}</p>
        <div v-if="$slots.actions" class="ct-public-hero-actions"><slot name="actions" /></div>
        <div v-if="$slots.note" class="ct-public-hero-note"><slot name="note" /></div>
      </div>
      <div v-if="$slots.default" class="min-w-0"><slot /></div>
    </div>
  </section>
</template>
