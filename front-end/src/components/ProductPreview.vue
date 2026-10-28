<script setup lang="ts">
import AppNavIcon from './AppNavIcon.vue'
const tasks = [
  {
    name: 'Enviar DCTFWeb',
    client: 'Comércio Silva',
    status: 'Em atraso',
    tone: 'bg-rose-50 text-rose-500',
  },
  {
    name: 'Conferir folha de pagamento',
    client: 'Mercado Boa Vista',
    status: 'Em andamento',
    tone: 'bg-blue-50 text-blue-500',
  },
  {
    name: 'Revisar apuração do mês',
    client: 'Clínica Saúde Mais',
    status: 'Pendente',
    tone: 'bg-amber-50 text-amber-600',
  },
]
const links = [
  { label: 'Início', icon: 'home' },
  { label: 'Obrigações', icon: 'clock' },
  { label: 'Calendário', icon: 'calendar' },
  { label: 'Clientes', icon: 'users' },
  { label: 'Documentos', icon: 'folder' },
]
</script>
<template>
  <figure>
    <div
      class="flex min-h-[370px] overflow-hidden rounded-2xl border border-blue-100 bg-[#f5f7fb] shadow-[0_20px_40px_#2337560d]"
    >
      <aside
        class="hidden w-[112px] shrink-0 flex-col border-r border-[#e8eef8] bg-[#fbfcfe] px-2 py-5 sm:flex"
      >
        <div class="mb-6 flex items-center gap-1.5 px-1 text-[10px] font-bold">
          <span class="flex h-4 w-4 items-center justify-center rounded bg-[#087cff] text-white"
            >✓</span
          ><span>Contably<span class="text-blue-500">Task</span></span>
        </div>
        <div
          v-for="(link, index) in links"
          :key="link.label"
          class="mb-2 flex items-center gap-2 rounded-md px-2 py-2 text-[9px]"
          :class="index === 0 ? 'bg-blue-50 text-blue-500' : 'text-slate-500'"
        >
          <AppNavIcon :name="link.icon" class="h-3 w-3 shrink-0" />{{ link.label }}
        </div>
      </aside>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-3 bg-white px-3 py-3">
          <span class="flex-1 rounded bg-[#f1f4f8] px-2 py-2 text-[9px] text-slate-400"
            >Buscar tarefas e clientes…</span
          ><span
            class="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 text-[9px] text-violet-600"
            >AS</span
          >
        </div>
        <div class="p-3">
          <p class="text-lg font-semibold">Olá, Ana!</p>
          <p class="mt-1 text-[10px] text-slate-500">Suas tarefas e prazos, em um só lugar.</p>
          <div class="my-4 grid grid-cols-3 gap-2">
            <div
              v-for="metric in [
                { value: 2, label: 'Em atraso', tone: 'text-rose-500' },
                { value: 8, label: 'Para hoje', tone: 'text-blue-500' },
                { value: 12, label: 'Concluídas', tone: 'text-emerald-500' },
              ]"
              :key="metric.label"
              class="rounded-lg bg-white p-2.5"
            >
              <strong class="text-lg" :class="metric.tone">{{ metric.value }}</strong>
              <p class="mt-1 text-[9px] text-slate-500">{{ metric.label }}</p>
            </div>
          </div>
          <div class="rounded-lg bg-white p-3">
            <p class="mb-2 text-[11px] font-semibold">Tarefas de hoje</p>
            <div
              v-for="task in tasks"
              :key="task.name"
              class="flex items-center justify-between gap-2 border-t border-slate-100 py-3 text-[9px]"
            >
              <div class="min-w-0">
                <p class="font-medium">{{ task.name }}</p>
                <p class="mt-1 text-slate-500">{{ task.client }}</p>
              </div>
              <span class="shrink-0 rounded-full px-1.5 py-1 text-[8px]" :class="task.tone">{{
                task.status
              }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <figcaption class="ct-public-example mt-3">Prévia ilustrativa com dados de exemplo.</figcaption>
  </figure>
</template>
