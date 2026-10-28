<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import PublicPageHero from '@/components/PublicPageHero.vue'
import PublicCallToAction from '@/components/PublicCallToAction.vue'
import AppNavIcon from '@/components/AppNavIcon.vue'
const principles = [
  {
    icon: 'home',
    title: 'Clareza para trabalhar',
    description:
      'Cada tela deve ajudar a encontrar o que importa e entender qual é o próximo passo.',
  },
  {
    icon: 'calendar',
    title: 'Uma rotina consistente',
    description:
      'Clientes, tarefas e prazos conectados para que a entrega não dependa de informações espalhadas.',
  },
  {
    icon: 'users',
    title: 'Espaço para crescer',
    description:
      'Uma organização que acompanha o crescimento da carteira, da equipe e da operação.',
  },
]
const connections = [
  {
    icon: 'users',
    title: 'Clientes organizados',
    description: 'Cada empresa com seus dados e histórico.',
  },
  {
    icon: 'clock',
    title: 'Tarefas com contexto',
    description: 'Prazo, prioridade e responsável no mesmo lugar.',
  },
  {
    icon: 'folder',
    title: 'Documentos à mão',
    description: 'Arquivos reunidos na pasta do cliente certo.',
  },
]
</script>

<template>
  <PublicLayout>
    <div class="ct-clarity-page">
      <PublicPageHero
        eyebrow="Sobre a ContablyTask"
        title="Mais clareza para a rotina contábil."
        description="A ContablyTask nasceu para reunir clientes, tarefas, prazos e documentos em um só lugar. Uma forma mais simples de organizar o escritório e acompanhar cada entrega."
      >
        <template #actions
          ><RouterLink to="/como-funciona" class="ct-button-primary"
            >Conheça a plataforma <span aria-hidden="true">→</span></RouterLink
          ></template
        >
        <div class="ct-public-illustration">
          <p class="mb-5 text-sm font-semibold text-slate-800">
            Seu escritório, trabalhando no mesmo fluxo
          </p>
          <div class="space-y-3">
            <div
              v-for="item in connections"
              :key="item.title"
              class="flex items-center gap-4 rounded-xl border border-blue-100 bg-white p-4"
            >
              <span class="ct-public-icon"><AppNavIcon :name="item.icon" /></span>
              <div class="min-w-0">
                <h2 class="text-sm font-semibold">{{ item.title }}</h2>
                <p class="mt-1 text-xs leading-5 text-slate-500">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </PublicPageHero>
      <section class="ct-public-section">
        <div class="ct-container grid items-start gap-10 lg:grid-cols-2 lg:gap-20">
          <div>
            <p class="ct-public-eyebrow">Por que existimos</p>
            <h2 class="ct-public-heading max-w-[19ch]">Organizar a rotina deveria ser simples.</h2>
          </div>
          <div class="ct-public-copy space-y-5">
            <p>
              Quando a carteira cresce, o trabalho costuma se dividir entre planilhas, mensagens,
              pastas e a memória da equipe. Fica mais difícil saber o que precisa ser feito, quem
              está cuidando de cada tarefa e qual prazo merece atenção.
            </p>
            <p>
              A ContablyTask reúne essas informações para dar continuidade ao trabalho. Cada cliente
              tem seu contexto, cada obrigação tem um responsável e os documentos acompanham a
              rotina do escritório.
            </p>
          </div>
        </div>
      </section>
      <section class="ct-public-section ct-public-section-soft">
        <div class="ct-container">
          <div class="ct-public-section-heading centered">
            <p class="ct-public-eyebrow">O que nos guia</p>
            <h2 class="ct-public-heading">Mais organização. Menos complicação.</h2>
          </div>
          <div class="grid gap-5 md:grid-cols-3">
            <article v-for="item in principles" :key="item.title" class="ct-public-card">
              <span class="ct-public-icon mb-5"><AppNavIcon :name="item.icon" /></span>
              <h3>{{ item.title }}</h3>
              <p class="mt-3">{{ item.description }}</p>
            </article>
          </div>
        </div>
      </section>
      <PublicCallToAction title="Conheça uma rotina com mais clareza." />
    </div>
  </PublicLayout>
</template>
