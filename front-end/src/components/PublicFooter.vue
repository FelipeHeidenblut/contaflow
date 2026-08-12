<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BrandMark from './BrandMark.vue'
</script>

<template>
  <footer class="border-t border-[var(--ct-border)] bg-white">
    <div class="ct-container grid gap-10 py-12 md:grid-cols-[1fr_auto_auto]">
      <div>
        <BrandMark />
        <p class="mt-4 max-w-sm text-sm leading-6 text-[var(--ct-text-muted)]">
          Rotina contábil organizada, com clientes, obrigações e documentos no mesmo fluxo.
        </p>
      </div>
      <div class="grid gap-2 text-sm">
        <p class="mb-1 font-semibold text-[var(--ct-ink)]">Produto</p>
        <RouterLink
          to="/como-funciona"
          class="text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]"
          >Como funciona</RouterLink
        >
        <RouterLink to="/planos" class="text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]"
          >Planos</RouterLink
        >
        <RouterLink to="/contato" class="text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]"
          >Contato</RouterLink
        >
      </div>
      <div class="grid gap-2 text-sm">
        <p class="mb-1 font-semibold text-[var(--ct-ink)]">Legal</p>
        <RouterLink to="/privacidade" class="text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]"
          >Privacidade</RouterLink
        >
        <RouterLink to="/termos" class="text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]"
          >Termos de uso</RouterLink
        >
      </div>
    </div>
    <div class="border-t border-[var(--ct-border)] py-5">
      <p class="ct-container text-xs text-[var(--ct-text-muted)]">
        © {{ new Date().getFullYear() }} ContablyTask.
      </p>
    </div>
  </footer>
</template>
