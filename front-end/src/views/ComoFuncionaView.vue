<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import PublicPageHero from '@/components/PublicPageHero.vue'
import PublicCallToAction from '@/components/PublicCallToAction.vue'
import ProductPreview from '@/components/ProductPreview.vue'
import AppNavIcon from '@/components/AppNavIcon.vue'
const steps = [
  {
    title: 'Organize seus clientes',
    description:
      'Cadastre ou importe sua carteira e reúna os dados de cada empresa em um só lugar.',
  },
  {
    title: 'Planeje as obrigações',
    description: 'Defina vencimento, prioridade, responsável e recorrência para cada entrega.',
  },
  {
    title: 'Acompanhe a execução',
    description:
      'Use a lista ou o Kanban para atualizar o andamento e sinalizar o que depende do cliente.',
  },
  {
    title: 'Mantenha o histórico',
    description:
      'Consulte as entregas e arquive tarefas concluídas para manter a rotina organizada.',
  },
]
const features = [
  {
    icon: 'calendar',
    title: 'Prazos sempre à vista',
    description:
      'Consulte vencimentos no calendário e acompanhe prioridades no dashboard. O link de calendário permite sincronizar com Google Agenda e Outlook.',
  },
  {
    icon: 'folder',
    title: 'Uma pasta para cada cliente',
    description:
      'Organize arquivos fiscais, contábeis e operacionais por cliente, com busca, categorias e acesso aos documentos.',
  },
  {
    icon: 'team',
    title: 'Responsabilidades claras',
    description:
      'Identifique quem cuida de cada cliente e tarefa. Os níveis de acesso acompanham o papel de cada pessoa na equipe.',
  },
]
</script>

<template>
  <PublicLayout>
    <div class="ct-clarity-page">
      <PublicPageHero
        eyebrow="Como funciona"
        title="Do cliente cadastrado à tarefa entregue."
        description="Um fluxo simples para organizar as demandas do escritório, acompanhar a equipe e encontrar o que precisa da sua atenção."
      >
        <template #actions
          ><RouterLink to="/cadastro" class="ct-button-primary"
            >Experimentar por 14 dias <span aria-hidden="true">→</span></RouterLink
          ><a href="#fluxo" class="ct-button-secondary">Veja como começar</a></template
        >
        <template #note>Sem cartão · Sem cobrança automática</template>
        <ProductPreview />
      </PublicPageHero>
      <section id="fluxo" class="ct-public-section scroll-mt-28">
        <div class="ct-container">
          <div class="ct-public-section-heading centered">
            <p class="ct-public-eyebrow">Um passo de cada vez</p>
            <h2 class="ct-public-heading">Uma rotina conectada, do início ao fim.</h2>
          </div>
          <ol class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <li v-for="(step, index) in steps" :key="step.title" class="ct-public-card">
              <span class="ct-public-step-number mb-5">{{ index + 1 }}</span>
              <h3>{{ step.title }}</h3>
              <p class="mt-3">{{ step.description }}</p>
            </li>
          </ol>
        </div>
      </section>
      <section class="ct-public-section ct-public-section-soft">
        <div class="ct-container">
          <div class="ct-public-section-heading">
            <p class="ct-public-eyebrow">No dia a dia</p>
            <h2 class="ct-public-heading">Tudo o que você precisa, no lugar certo.</h2>
            <p class="ct-public-copy mt-4">
              Tarefas, clientes, equipe e documentos fazem parte do mesmo fluxo.
            </p>
          </div>
          <div class="grid gap-5 md:grid-cols-3">
            <article v-for="feature in features" :key="feature.title" class="ct-public-card">
              <span class="ct-public-icon mb-5"><AppNavIcon :name="feature.icon" /></span>
              <h3>{{ feature.title }}</h3>
              <p class="mt-3">{{ feature.description }}</p>
            </article>
          </div>
          <div class="mt-8 text-center">
            <RouterLink to="/planos" class="ct-public-link"
              >Compare os recursos de cada plano <span aria-hidden="true">→</span></RouterLink
            >
          </div>
        </div>
      </section>
      <PublicCallToAction title="Comece pela próxima entrega do seu escritório." />
    </div>
  </PublicLayout>
</template>
