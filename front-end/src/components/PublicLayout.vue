<script setup lang="ts">
import PublicHeader from './PublicHeader.vue'
import PublicFooter from './PublicFooter.vue'
</script>

<template>
  <div class="ct-public-page min-h-screen bg-[var(--ct-bg)] text-[var(--ct-ink)]">
    <PublicHeader />
    <main><slot /></main>
    <PublicFooter />
  </div>
</template>
