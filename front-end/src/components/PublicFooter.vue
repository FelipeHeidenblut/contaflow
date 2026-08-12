<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BrandMark from './BrandMark.vue'
</script>

<template>
  <footer class="overflow-hidden bg-[var(--ct-navy)] text-white">
    <div class="ct-container grid gap-12 py-14 md:grid-cols-[1fr_auto_auto] lg:py-16">
      <div>
        <BrandMark inverse />
        <p class="mt-5 max-w-sm text-sm leading-6 text-white/55">
          Rotina contábil organizada, com clientes, obrigações e documentos no mesmo fluxo.
        </p>
        <RouterLink to="/cadastro" class="ct-link-arrow mt-6 text-blue-200">
          Criar meu escritório <span>→</span>
        </RouterLink>
      </div>
      <div class="grid gap-2 text-sm">
        <p
          class="mb-2 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-white/35"
        >
          Produto
        </p>
        <RouterLink to="/como-funciona" class="py-1 text-white/60 hover:text-white"
          >Como funciona</RouterLink
        >
        <RouterLink to="/planos" class="py-1 text-white/60 hover:text-white">Planos</RouterLink>
        <RouterLink to="/contato" class="py-1 text-white/60 hover:text-white">Contato</RouterLink>
      </div>
      <div class="grid gap-2 text-sm">
        <p
          class="mb-2 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-white/35"
        >
          Legal
        </p>
        <RouterLink to="/privacidade" class="py-1 text-white/60 hover:text-white"
          >Privacidade</RouterLink
        >
        <RouterLink to="/termos" class="py-1 text-white/60 hover:text-white"
          >Termos de uso</RouterLink
        >
      </div>
    </div>
    <div class="ct-container pointer-events-none select-none overflow-hidden" aria-hidden="true">
      <p
        class="translate-y-[18%] bg-gradient-to-b from-white/[0.08] to-white/0 bg-clip-text text-[clamp(5rem,16vw,12rem)] font-bold leading-[0.75] tracking-[-0.065em] text-transparent"
      >
        ContablyTask
      </p>
    </div>
    <div class="border-t border-white/10 py-5">
      <div class="ct-container flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs text-white/35">© {{ new Date().getFullYear() }} ContablyTask.</p>
        <RouterLink to="/" class="text-xs text-white/35 hover:text-white"
          >Voltar ao topo ↑</RouterLink
        >
      </div>
    </div>
  </footer>
</template>
