<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'

const steps = [
  [
    'Clientes',
    'Cadastre manualmente ou importe sua carteira para reunir as informações essenciais de cada empresa.',
  ],
  ['Obrigações', 'Crie demandas, defina vencimento, importância, responsável e recorrência.'],
  ['Execução', 'A equipe atualiza o andamento e sinaliza quando depende de informação do cliente.'],
  ['Controle', 'O dashboard e o calendário mostram prioridades, atrasos e próximas entregas.'],
]
const features = [
  [
    'Calendário compartilhável',
    'Sincronize prazos com Google Agenda e Outlook por um link seguro.',
  ],
  [
    'Documentos por cliente',
    'Encontre arquivos fiscais, contábeis e operacionais sem procurar em pastas dispersas.',
  ],
  [
    'Responsabilidade visível',
    'Saiba quem está cuidando de cada entrega e como o trabalho está distribuído.',
  ],
]
</script>

<template>
  <PublicLayout>
    <section class="border-b border-[var(--ct-border)] bg-white">
      <div
        class="ct-container grid items-center gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:gap-16 lg:py-24"
      >
        <div>
          <p class="ct-eyebrow">Como funciona</p>
          <h1 class="ct-display mt-5">Do cliente cadastrado à obrigação entregue.</h1>
          <p class="ct-body-lg mt-6">
            Um fluxo direto para organizar a operação sem exigir uma implantação longa ou processos
            artificiais.
          </p>
          <RouterLink to="/cadastro" class="ct-button-primary mt-8">Começar grátis</RouterLink>
        </div>

        <div class="overflow-hidden rounded-xl border border-slate-300 bg-[var(--ct-bg)]">
          <div
            class="flex items-center justify-between border-b border-[var(--ct-border)] bg-white px-5 py-4"
          >
            <div>
              <p class="text-xs font-semibold text-[var(--ct-ink)]">Fluxo de uma obrigação</p>
              <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">Grupo Horizonte · Agosto</p>
            </div>
            <span
              class="rounded-md bg-[var(--ct-primary-soft)] px-2 py-1 text-[10px] font-semibold text-[var(--ct-primary)]"
              >Em andamento</span
            >
          </div>

          <ol class="px-5 py-2">
            <li
              class="grid grid-cols-[1.5rem_1fr_auto] items-center gap-3 border-b border-[var(--ct-border)] py-4"
            >
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-700"
                aria-hidden="true"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </span>
              <div>
                <p class="text-xs font-semibold text-[var(--ct-ink)]">Cliente cadastrado</p>
                <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">
                  Dados e regime tributário centralizados
                </p>
              </div>
              <span class="text-[10px] font-medium text-emerald-700">Concluído</span>
            </li>
            <li
              class="grid grid-cols-[1.5rem_1fr_auto] items-center gap-3 border-b border-[var(--ct-border)] py-4"
            >
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-700"
                aria-hidden="true"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </span>
              <div>
                <p class="text-xs font-semibold text-[var(--ct-ink)]">DCTFWeb criada</p>
                <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">
                  Prazo, importância e recorrência definidos
                </p>
              </div>
              <span class="text-[10px] font-medium text-emerald-700">Concluído</span>
            </li>
            <li
              class="grid grid-cols-[1.5rem_1fr_auto] items-center gap-3 border-b border-[var(--ct-border)] py-4"
            >
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--ct-primary)] text-[10px] font-semibold text-white"
                >3</span
              >
              <div>
                <p class="text-xs font-semibold text-[var(--ct-ink)]">Execução pela equipe</p>
                <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">Responsável: Ana Costa</p>
              </div>
              <span class="text-[10px] font-medium text-[var(--ct-primary)]">Agora</span>
            </li>
            <li class="grid grid-cols-[1.5rem_1fr_auto] items-center gap-3 py-4 opacity-60">
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full border border-slate-300 bg-white text-[10px] font-semibold text-slate-500"
                >4</span
              >
              <div>
                <p class="text-xs font-semibold text-[var(--ct-ink)]">Entrega e histórico</p>
                <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">
                  Vencimento em 21 de agosto
                </p>
              </div>
              <span class="text-[10px] font-medium text-slate-500">Próxima</span>
            </li>
          </ol>

          <div class="grid grid-cols-2 border-t border-[var(--ct-border)] bg-white">
            <div class="border-r border-[var(--ct-border)] px-5 py-3">
              <span class="text-[10px] text-[var(--ct-text-muted)]">Documentos</span
              ><strong class="ml-2 text-xs text-[var(--ct-ink)]">4 anexos</strong>
            </div>
            <div class="px-5 py-3">
              <span class="text-[10px] text-[var(--ct-text-muted)]">Atualização</span
              ><strong class="ml-2 text-xs text-[var(--ct-ink)]">há 12 min</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="ct-section">
      <div class="ct-container grid gap-14 lg:grid-cols-[0.7fr_1.3fr]">
        <div>
          <p class="ct-eyebrow">Fluxo principal</p>
          <h2 class="ct-section-title mt-4">Quatro etapas, um só contexto.</h2>
        </div>
        <ol class="border-t border-[var(--ct-border)]">
          <li
            v-for="(step, i) in steps"
            :key="step[0]"
            class="grid gap-4 border-b border-[var(--ct-border)] py-7 sm:grid-cols-[3rem_11rem_1fr]"
          >
            <span class="text-xs font-semibold text-[var(--ct-primary)]">0{{ i + 1 }}</span>
            <h3 class="font-semibold">{{ step[0] }}</h3>
            <p class="text-sm leading-6 text-[var(--ct-text-muted)]">{{ step[1] }}</p>
          </li>
        </ol>
      </div>
    </section>
    <section class="border-y border-[var(--ct-border)] bg-white">
      <div class="ct-container py-16 lg:py-20">
        <p class="ct-eyebrow">No dia a dia</p>
        <h2 class="ct-section-title mt-4">Recursos que permanecem discretos até você precisar.</h2>
        <div
          class="mt-12 grid gap-px overflow-hidden rounded-xl border border-[var(--ct-border)] bg-[var(--ct-border)] md:grid-cols-3"
        >
          <article v-for="feature in features" :key="feature[0]" class="bg-white p-6">
            <h3 class="font-semibold">{{ feature[0] }}</h3>
            <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">{{ feature[1] }}</p>
          </article>
        </div>
      </div>
    </section>
    <section class="ct-section">
      <div class="ct-container flex flex-col justify-between gap-8 md:flex-row md:items-end">
        <div>
          <h2 class="ct-section-title">Veja se funciona para o seu escritório.</h2>
          <p class="ct-body-lg mt-4">Você pode começar com até cinco clientes no plano gratuito.</p>
        </div>
        <div class="flex gap-3">
          <RouterLink to="/planos" class="ct-button-secondary">Ver planos</RouterLink
          ><RouterLink to="/cadastro" class="ct-button-primary">Criar conta</RouterLink>
        </div>
      </div>
    </section>
  </PublicLayout>
</template>
