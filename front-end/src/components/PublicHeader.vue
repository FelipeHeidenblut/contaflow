<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import BrandMark from './BrandMark.vue'

const route = useRoute()
const open = ref(false)
const links = [
  { label: 'Produto', to: '/como-funciona' },
  { label: 'Planos', to: '/planos' },
  { label: 'Sobre', to: '/sobre' },
  { label: 'Contato', to: '/contato' },
]
</script>

<template>
  <header
    class="sticky top-0 z-50 border-b border-[var(--ct-border)] bg-white/90 shadow-[0_1px_0_rgba(15,23,42,0.02)] backdrop-blur-xl"
  >
    <div class="ct-container flex h-[72px] items-center justify-between">
      <RouterLink to="/" aria-label="Página inicial"><BrandMark /></RouterLink>
      <nav class="hidden items-center gap-1 md:flex" aria-label="Navegação principal">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="rounded-lg px-3.5 py-2 text-[13px] font-medium transition-colors"
          :class="
            route.path === link.to
              ? 'bg-blue-50 text-[var(--ct-primary)]'
              : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'
          "
        >
          {{ link.label }}
        </RouterLink>
      </nav>
      <div class="hidden items-center gap-2 md:flex">
        <RouterLink to="/login" class="ct-button-secondary rounded-xl">Entrar</RouterLink>
        <RouterLink to="/cadastro" class="ct-button-primary rounded-xl">
          Testar grátis
          <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-width="2" d="M5 12h14m-6-6 6 6-6 6" />
          </svg>
        </RouterLink>
      </div>
      <button
        class="rounded-xl border border-[var(--ct-border)] p-2.5 text-[var(--ct-ink)] md:hidden"
        type="button"
        :aria-expanded="open"
        aria-label="Abrir menu"
        @click="open = !open"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-width="2"
            :d="open ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'"
          />
        </svg>
      </button>
    </div>
    <div v-if="open" class="border-t border-[var(--ct-border)] bg-white px-4 py-4 md:hidden">
      <nav class="mx-auto flex max-w-md flex-col" aria-label="Navegação móvel">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="rounded-lg px-3 py-3 text-sm font-medium"
          :class="route.path === link.to ? 'bg-blue-50 text-[var(--ct-primary)]' : 'text-slate-700'"
          @click="open = false"
          >{{ link.label }}</RouterLink
        >
        <div class="mt-3 grid grid-cols-2 gap-2 border-t border-[var(--ct-border)] pt-4">
          <RouterLink to="/login" class="ct-button-secondary rounded-xl" @click="open = false"
            >Entrar</RouterLink
          >
          <RouterLink to="/cadastro" class="ct-button-primary rounded-xl" @click="open = false"
            >Testar grátis</RouterLink
          >
        </div>
      </nav>
    </div>
  </header>
</template>
