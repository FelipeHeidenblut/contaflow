<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-[var(--ct-bg)] px-6 text-center">
    <div>
      <p class="text-sm font-bold uppercase tracking-[.18em] text-[var(--ct-primary)]">Erro 404</p>
      <h1 class="mt-3 text-4xl font-semibold tracking-tight text-[var(--ct-ink)]">
        Página não encontrada
      </h1>
      <p class="mx-auto mt-3 max-w-md text-sm leading-relaxed text-[var(--ct-text-muted)]">
        O endereço pode estar incorreto ou a página pode ter sido movida.
      </p>
      <RouterLink
        to="/"
        class="mt-7 inline-flex rounded-xl bg-[var(--ct-primary)] px-5 py-3 text-sm font-semibold text-white hover:bg-[var(--ct-primary-hover)]"
        >Voltar ao início</RouterLink
      >
    </div>
  </main>
</template>
