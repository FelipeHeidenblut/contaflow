<script setup lang="ts">
import { RouterLink } from 'vue-router'
withDefaults(defineProps<{ title?: string; description?: string }>(), {
  title: 'Menos planilhas. Mais tempo para o que importa.',
  description:
    'Experimente o Profissional por 14 dias e veja como organizar a rotina do seu escritório.',
})
</script>

<template>
  <section class="ct-public-section">
    <div class="ct-container">
      <div class="ct-public-cta">
        <div>
          <p class="ct-public-eyebrow">Seu próximo passo</p>
          <h2>{{ title }}</h2>
          <p>{{ description }}</p>
        </div>
        <div class="ct-public-cta-action">
          <RouterLink to="/cadastro" class="ct-button-primary"
            >Começar meu teste grátis <span aria-hidden="true">→</span></RouterLink
          ><span>Sem cartão · Sem cobrança automática</span>
        </div>
      </div>
    </div>
  </section>
</template>
