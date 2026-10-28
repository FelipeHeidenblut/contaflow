<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BrandMark from './BrandMark.vue'
const links = [
  { label: 'Como funciona', to: '/como-funciona' },
  { label: 'Preços', to: '/planos' },
  { label: 'Sobre', to: '/sobre' },
  { label: 'Contato', to: '/contato' },
  { label: 'Privacidade', to: '/privacidade' },
  { label: 'Termos de uso', to: '/termos' },
]
</script>
<template>
  <footer class="border-t border-blue-100 bg-white py-7 text-slate-500">
    <div class="ct-container">
      <div class="flex flex-wrap items-center justify-between gap-5">
        <RouterLink to="/" aria-label="ContablyTask, início"><BrandMark /></RouterLink>
        <p class="text-xs leading-6">
          Mais clareza para a rotina contábil. © {{ new Date().getFullYear() }}
        </p>
      </div>
      <nav aria-label="Links do rodapé" class="mt-5 flex flex-wrap gap-x-6 gap-y-3 text-xs">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="hover:text-blue-600"
          >{{ link.label }}</RouterLink
        >
      </nav>
    </div>
  </footer>
</template>
