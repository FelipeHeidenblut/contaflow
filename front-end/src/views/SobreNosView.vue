<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'

const principles = [
  [
    'Clareza antes de complexidade',
    'Cada tela deve ajudar o usuário a decidir o próximo passo sem exigir treinamento extenso.',
  ],
  [
    'Processo antes de improviso',
    'A tecnologia precisa sustentar uma rotina consistente, não criar mais uma tarefa para a equipe.',
  ],
  [
    'Evolução com o escritório',
    'O produto começa simples e acompanha o crescimento da carteira, da equipe e da operação.',
  ],
]
</script>

<template>
  <PublicLayout>
    <section class="border-b border-[var(--ct-border)] bg-white">
      <div class="ct-container grid gap-12 py-16 lg:grid-cols-[1fr_0.8fr] lg:py-24">
        <div>
          <p class="ct-eyebrow">Sobre a ContablyTask</p>
          <h1 class="ct-display mt-5">
            Software contábil deve reduzir ruído, não adicionar camadas.
          </h1>
        </div>
        <p class="ct-body-lg self-end">
          Criamos a ContablyTask para dar visibilidade à rotina de escritórios que ainda precisam
          conciliar planilhas, mensagens, pastas e memória para entregar no prazo.
        </p>
      </div>
    </section>
    <section class="ct-section">
      <div class="ct-container grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <p class="ct-eyebrow">O problema</p>
          <h2 class="ct-section-title mt-4">A operação cresce antes do processo.</h2>
        </div>
        <div class="space-y-6 text-base leading-7 text-[var(--ct-text-muted)]">
          <p>
            Quando a carteira aumenta, tarefas passam a depender de planilhas paralelas, conversas
            no WhatsApp e conhecimento concentrado em poucas pessoas.
          </p>
          <p>
            A ContablyTask cria uma base operacional comum: cada cliente tem contexto, cada
            obrigação tem responsável e prazo, e cada documento pode ser encontrado no mesmo fluxo.
          </p>
        </div>
      </div>
    </section>
    <section class="border-y border-[var(--ct-border)] bg-white">
      <div class="ct-container py-16 lg:py-20">
        <p class="ct-eyebrow">Como pensamos</p>
        <h2 class="ct-section-title mt-4">Princípios de produto.</h2>
        <div
          class="mt-12 grid border-y border-[var(--ct-border)] md:grid-cols-3 md:divide-x md:divide-[var(--ct-border)]"
        >
          <article
            v-for="(item, i) in principles"
            :key="item[0]"
            class="border-b border-[var(--ct-border)] py-7 md:border-b-0 md:px-7 md:first:pl-0 md:last:pr-0"
          >
            <p class="text-xs font-semibold text-[var(--ct-primary)]">0{{ i + 1 }}</p>
            <h3 class="mt-5 font-semibold">{{ item[0] }}</h3>
            <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">{{ item[1] }}</p>
          </article>
        </div>
      </div>
    </section>
    <section class="ct-section">
      <div class="ct-container flex flex-col justify-between gap-8 md:flex-row md:items-center">
        <div>
          <h2 class="text-2xl font-semibold tracking-tight">Conheça a plataforma na prática.</h2>
          <p class="mt-2 text-sm text-[var(--ct-text-muted)]">
            Comece gratuitamente e organize a sua próxima rotina mensal.
          </p>
        </div>
        <RouterLink to="/cadastro" class="ct-button-primary">Criar conta</RouterLink>
      </div>
    </section>
  </PublicLayout>
</template>
