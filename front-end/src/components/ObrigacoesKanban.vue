<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchPage } from '../services/pagination'
import type { Obrigacao, TaskStatus } from '../types/obrigacao'

const props = defineProps<{
  filters: Record<string, string | number | undefined>
  refreshKey: number
  updating: boolean
  clientName: (id: string | number) => string
  memberName: (id?: string | number | null) => string
  overdue: (date: string, status: string) => boolean
  formatDate: (date: string) => string
}>()
const emit = defineEmits<{
  details: [task: Obrigacao]
  move: [task: Obrigacao, status: TaskStatus]
}>()

const columns: { status: TaskStatus; label: string; color: string }[] = [
  { status: 'pendente', label: 'A fazer', color: 'bg-slate-400' },
  { status: 'em_andamento', label: 'Em andamento', color: 'bg-[var(--ct-primary)]' },
  { status: 'aguardando_cliente', label: 'Aguardando cliente', color: 'bg-amber-500' },
  { status: 'concluida', label: 'Concluído', color: 'bg-emerald-500' },
]
interface ColumnState {
  items: Obrigacao[]
  total: number | null
  page: number
  pages: number
  loading: boolean
  error: boolean
}
const state = ref<Record<string, ColumnState>>({})
const draggedTask = ref<Obrigacao | null>(null)
const activeDrop = ref<TaskStatus | null>(null)
const visibleColumns = computed(() =>
  columns.filter(
    (column) => !props.filters.task_status || column.status === props.filters.task_status,
  ),
)
let generation = 0

async function loadColumn(status: TaskStatus, version = generation) {
  const column = state.value[status]
  if (!column || column.loading) return
  column.loading = true
  column.error = false
  try {
    const result = await fetchPage<Obrigacao>('/api/v1/obrigacoes', column.page + 1, 20, {
      ...props.filters,
      task_status: status,
    })
    if (version !== generation) return
    const knownIds = new Set(column.items.map((task) => task.id))
    column.items.push(...result.items.filter((task) => !knownIds.has(task.id)))
    column.total = result.total
    column.page = result.page
    column.pages = result.pages
  } catch {
    if (version === generation) column.error = true
  } finally {
    if (version === generation) column.loading = false
  }
}

watch(
  [() => props.filters, () => props.refreshKey],
  () => {
    generation += 1
    draggedTask.value = null
    activeDrop.value = null
    state.value = Object.fromEntries(
      columns.map(({ status }) => [
        status,
        { items: [], total: null, page: 0, pages: 0, loading: false, error: false },
      ]),
    )
    for (const column of visibleColumns.value) void loadColumn(column.status)
  },
  { immediate: true },
)

function startDrag(event: DragEvent, task: Obrigacao) {
  if (props.updating || task.type === 'receita_federal') {
    event.preventDefault()
    return
  }
  draggedTask.value = task
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(task.id))
  }
}

function dragOver(event: DragEvent, status: TaskStatus) {
  if (!draggedTask.value || props.updating || draggedTask.value.status === status) return
  event.preventDefault()
  activeDrop.value = status
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
}

function endDrag() {
  draggedTask.value = null
  activeDrop.value = null
}

function dropTask(status: TaskStatus) {
  const task = draggedTask.value
  endDrag()
  if (task && !props.updating && task.status !== status) emit('move', task, status)
}

function selectStatus(event: Event, task: Obrigacao) {
  const select = event.target as HTMLSelectElement
  const status = select.value as TaskStatus
  select.value = task.status
  if (status !== task.status && !props.updating) emit('move', task, status)
}
</script>

<template>
  <section aria-label="Quadro Kanban de obrigações" :aria-busy="updating">
    <p class="mb-3 text-xs text-[var(--ct-text-muted)]" role="status">
      {{
        updating
          ? 'Salvando alteração…'
          : 'Arraste os cartões ou use a opção de status em cada tarefa.'
      }}
    </p>
    <div class="flex items-start gap-4 overflow-x-auto pb-4">
      <section
        v-for="column in visibleColumns"
        :key="column.status"
        :aria-labelledby="`kanban-${column.status}`"
        class="min-w-[280px] flex-1 rounded-xl border p-3 transition-colors sm:min-w-[300px]"
        :class="
          activeDrop === column.status
            ? 'border-[var(--ct-primary)] bg-[var(--ct-primary-soft)]'
            : 'border-[var(--ct-border)] bg-slate-50'
        "
        @dragover="dragOver($event, column.status)"
        @dragleave.self="activeDrop = null"
        @drop.prevent="dropTask(column.status)"
      >
        <header class="mb-4 flex items-center gap-2 px-1">
          <span :class="column.color" class="h-2.5 w-2.5 rounded-full" aria-hidden="true"></span>
          <h2 :id="`kanban-${column.status}`" class="text-sm font-semibold text-[var(--ct-ink)]">
            {{ column.label }}
          </h2>
          <span class="ml-auto rounded-full bg-white px-2 py-0.5 text-xs text-slate-600">
            {{ state[column.status]?.total ?? '—' }}
          </span>
        </header>
        <div class="min-h-32 space-y-3">
          <article
            v-for="task in state[column.status]?.items"
            :key="task.id"
            :draggable="!updating && task.type !== 'receita_federal'"
            class="rounded-lg border border-[var(--ct-border)] bg-white p-4 shadow-sm"
            :class="{ 'opacity-50': draggedTask?.id === task.id, 'cursor-grab': !updating }"
            @dragstart="startDrag($event, task)"
            @dragend="endDrag"
          >
            <button
              type="button"
              class="w-full text-left focus-visible:outline-2 focus-visible:outline-[var(--ct-primary)]"
              :aria-label="`Ver detalhes de ${task.title}`"
              @click="emit('details', task)"
            >
              <span class="block break-words text-sm font-semibold text-[var(--ct-ink)]">{{
                task.title
              }}</span>
              <span class="mt-1 block break-words text-xs text-[var(--ct-text-muted)]">{{
                clientName(task.client_id)
              }}</span>
            </button>
            <div class="mt-3 flex flex-wrap gap-2 text-[11px] font-medium">
              <span
                class="rounded border px-2 py-0.5"
                :class="
                  task.grau_importancia === 'Urgente' || task.grau_importancia === 'Alta'
                    ? 'border-orange-200 bg-orange-50 text-orange-700'
                    : 'border-slate-200 bg-slate-50 text-slate-600'
                "
              >
                {{ task.grau_importancia || 'Média' }}
              </span>
              <span
                v-if="task.is_recurring"
                class="rounded bg-[var(--ct-primary-soft)] px-2 py-0.5 text-[var(--ct-primary)]"
                >Recorrente</span
              >
              <span
                v-if="overdue(task.due_date, task.status)"
                class="rounded bg-red-50 px-2 py-0.5 text-red-700"
                >Atrasada</span
              >
            </div>
            <p
              class="mt-3 text-xs"
              :class="
                overdue(task.due_date, task.status)
                  ? 'font-semibold text-red-600'
                  : 'text-slate-600'
              "
            >
              Prazo: {{ formatDate(task.due_date) }}
            </p>
            <p class="mt-1 break-words text-xs text-[var(--ct-text-muted)]">
              {{ memberName(task.assigned_to) }}
            </p>
            <select
              :value="task.status"
              :disabled="updating || task.type === 'receita_federal'"
              :aria-label="`Status de ${task.title}`"
              class="mt-3 w-full rounded-lg border border-[var(--ct-border)] bg-white px-2 py-2 text-xs text-[var(--ct-ink)] disabled:opacity-50"
              @change="selectStatus($event, task)"
            >
              <option
                v-for="destination in columns"
                :key="destination.status"
                :value="destination.status"
              >
                {{ destination.label }}
              </option>
            </select>
          </article>
          <p
            v-if="state[column.status]?.loading"
            role="status"
            class="p-4 text-center text-xs text-slate-500"
          >
            Carregando tarefas…
          </p>
          <div v-else-if="state[column.status]?.error" class="p-3 text-center">
            <p role="alert" class="mb-2 text-xs text-red-700">
              Não foi possível carregar esta coluna.
            </p>
            <button
              type="button"
              class="text-xs font-semibold text-[var(--ct-primary)]"
              @click="loadColumn(column.status)"
            >
              Tentar novamente
            </button>
          </div>
          <p
            v-else-if="!state[column.status]?.items.length"
            class="rounded-lg border border-dashed border-slate-300 p-6 text-center text-xs text-slate-500"
          >
            Nenhuma tarefa nesta etapa.
          </p>
          <button
            v-else-if="(state[column.status]?.page ?? 0) < (state[column.status]?.pages ?? 0)"
            type="button"
            class="w-full rounded-lg border border-[var(--ct-border)] bg-white py-2 text-xs font-semibold text-[var(--ct-primary)]"
            @click="loadColumn(column.status)"
          >
            Carregar mais ({{ state[column.status]?.items.length }} de
            {{ state[column.status]?.total }})
          </button>
        </div>
      </section>
    </div>
  </section>
</template>
