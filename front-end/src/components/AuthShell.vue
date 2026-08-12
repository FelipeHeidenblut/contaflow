<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BrandMark from './BrandMark.vue'

withDefaults(defineProps<{ title: string; description: string; wide?: boolean }>(), { wide: false })
</script>

<template>
  <div class="min-h-screen bg-white text-[var(--ct-ink)]">
    <div class="grid min-h-screen lg:grid-cols-[0.82fr_1.18fr]">
      <aside
        class="hidden flex-col justify-between bg-[var(--ct-navy)] p-10 text-white lg:flex xl:p-14"
      >
        <RouterLink to="/" class="w-fit"><BrandMark inverse /></RouterLink>
        <div class="max-w-md">
          <p class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--ct-accent)]">
            Rotina contábil organizada
          </p>
          <p class="mt-5 text-3xl font-semibold leading-tight tracking-[-0.035em]">
            Clientes, prazos e documentos no mesmo fluxo de trabalho.
          </p>
          <div class="mt-8 border-t border-white/15 pt-6 text-sm leading-6 text-white/60">
            Comece com o essencial e adicione estrutura conforme o escritório cresce.
          </div>
        </div>
        <p class="text-xs text-white/40">ContablyTask · Gestão operacional</p>
      </aside>
      <main class="flex min-h-screen flex-col">
        <div
          class="flex h-16 items-center justify-between border-b border-[var(--ct-border)] px-5 lg:hidden"
        >
          <RouterLink to="/"><BrandMark /></RouterLink><slot name="mobile-action" />
        </div>
        <div class="flex flex-1 items-center justify-center px-5 py-10 sm:px-8">
          <div class="w-full" :class="wide ? 'max-w-xl' : 'max-w-md'">
            <div class="mb-8">
              <h1 class="text-3xl font-semibold tracking-[-0.035em]">{{ title }}</h1>
              <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">{{ description }}</p>
            </div>
            <slot />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
