<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { toast } from 'vue3-toastify'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { getApiErrorMessage } from '../utils/apiError'

interface CommentItem {
  id: string
  client_id: string
  task_id: string | null
  author_id: string | null
  author_name: string
  content: string
  created_at: string
}

const props = defineProps<{
  clientId: string | number
  taskId?: string | number | null
}>()

const authStore = useAuthStore()
const comments = ref<CommentItem[]>([])
const content = ref('')
const isLoading = ref(true)
const isSaving = ref(false)
const deletingId = ref<string | null>(null)

const canManage = computed(() => ['admin', 'gerente'].includes(authStore.role))

const initials = (name: string) => {
  const parts = name.trim().split(/\s+/)
  return `${parts[0]?.[0] || '?'}${parts.length > 1 ? parts.at(-1)?.[0] || '' : ''}`.toUpperCase()
}

const formatDate = (value: string) =>
  new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))

const loadComments = async () => {
  if (!props.clientId) return
  isLoading.value = true
  try {
    const { data } = await api.get<CommentItem[]>('/api/v1/comentarios', {
      params: {
        client_id: props.clientId,
        ...(props.taskId ? { task_id: props.taskId } : {}),
      },
    })
    comments.value = data
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível carregar os comentários.'))
  } finally {
    isLoading.value = false
  }
}

const addComment = async () => {
  const normalized = content.value.trim()
  if (!normalized) return
  isSaving.value = true
  try {
    const { data } = await api.post<CommentItem>('/api/v1/comentarios', {
      client_id: props.clientId,
      task_id: props.taskId || null,
      content: normalized,
    })
    comments.value.push(data)
    content.value = ''
    toast.success('Comentário publicado.')
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível publicar o comentário.'))
  } finally {
    isSaving.value = false
  }
}

const deleteComment = async (comment: CommentItem) => {
  deletingId.value = comment.id
  try {
    await api.delete(`/api/v1/comentarios/${comment.id}`)
    comments.value = comments.value.filter((item) => item.id !== comment.id)
    toast.success('Comentário removido.')
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível remover o comentário.'))
  } finally {
    deletingId.value = null
  }
}

watch(() => [props.clientId, props.taskId], loadComments)
onMounted(loadComments)
</script>

<template>
  <section class="space-y-4" aria-label="Comentários internos">
    <form
      class="rounded-xl border border-[var(--ct-border)] bg-slate-50/70 p-3"
      @submit.prevent="addComment"
    >
      <label class="sr-only" for="internal-comment">Adicionar comentário interno</label>
      <textarea
        id="internal-comment"
        v-model="content"
        maxlength="2000"
        rows="3"
        placeholder="Deixe uma observação para a equipe..."
        class="w-full resize-none border-0 bg-transparent text-sm leading-6 text-[var(--ct-ink)] outline-none placeholder:text-slate-400 focus:ring-0"
      ></textarea>
      <div
        class="mt-2 flex items-center justify-between gap-3 border-t border-[var(--ct-border)] pt-3"
      >
        <span class="text-[11px] text-[var(--ct-text-muted)]"
          >Visível apenas para o escritório</span
        >
        <button
          type="submit"
          class="ct-button-primary min-h-9 px-3 text-xs"
          :disabled="isSaving || !content.trim()"
        >
          {{ isSaving ? 'Publicando...' : 'Publicar' }}
        </button>
      </div>
    </form>

    <div v-if="isLoading" class="space-y-3">
      <div v-for="index in 2" :key="index" class="h-20 animate-pulse rounded-xl bg-slate-100"></div>
    </div>

    <div
      v-else-if="comments.length === 0"
      class="rounded-xl border border-dashed border-[var(--ct-border)] px-4 py-8 text-center"
    >
      <p class="text-sm font-medium text-[var(--ct-ink)]">Nenhuma observação ainda</p>
      <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
        O primeiro comentário inicia o histórico interno.
      </p>
    </div>

    <ol v-else class="space-y-3">
      <li v-for="comment in comments" :key="comment.id" class="flex gap-3">
        <span
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-[10px] font-bold text-[var(--ct-primary)]"
        >
          {{ initials(comment.author_name) }}
        </span>
        <div class="min-w-0 flex-1 rounded-xl border border-[var(--ct-border)] bg-white p-3">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold text-[var(--ct-ink)]">{{ comment.author_name }}</p>
              <time class="text-[11px] text-[var(--ct-text-muted)]">{{
                formatDate(comment.created_at)
              }}</time>
            </div>
            <button
              v-if="comment.author_id === authStore.userId || canManage"
              type="button"
              class="text-[11px] font-medium text-slate-400 hover:text-red-600"
              :disabled="deletingId === comment.id"
              @click="deleteComment(comment)"
            >
              {{ deletingId === comment.id ? 'Removendo...' : 'Remover' }}
            </button>
          </div>
          <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-[#3f4d65]">
            {{ comment.content }}
          </p>
        </div>
      </li>
    </ol>
  </section>
</template>
