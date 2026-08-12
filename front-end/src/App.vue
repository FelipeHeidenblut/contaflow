<script setup lang="ts">
import { ref } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import CookiesView from './components/CookiesView.vue'

const router = useRouter()
const isNavigating = ref(false)

router.beforeEach(() => {
  isNavigating.value = true
})
router.afterEach(() => {
  isNavigating.value = false
})
router.onError(() => {
  isNavigating.value = false
})
</script>

<template>
  <div>
    <div
      v-if="isNavigating"
      class="fixed inset-x-0 top-0 z-[200] h-1 overflow-hidden bg-[var(--ct-primary-soft)]"
      role="progressbar"
      aria-label="Carregando página"
    >
      <div class="h-full w-1/2 animate-pulse bg-[var(--ct-primary)]"></div>
    </div>
    <RouterView />
    <CookiesView />
  </div>
</template>
