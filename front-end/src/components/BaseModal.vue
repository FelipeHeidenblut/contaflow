<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    size?: 'sm' | 'md' | 'lg' | 'xl'
    closeOnBackdrop?: boolean
  }>(),
  { size: 'md', closeOnBackdrop: true },
)

const emit = defineEmits<{ close: [] }>()
const panel = ref<HTMLElement | null>(null)
let previousFocus: HTMLElement | null = null

const sizes = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-2xl', xl: 'max-w-4xl' }
const close = () => emit('close')

const onKeydown = (event: KeyboardEvent) => {
  if (!props.open) return
  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }
  if (event.key !== 'Tab' || !panel.value) return
  const focusable = Array.from(
    panel.value.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  )
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last?.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first?.focus()
  }
}

watch(
  () => props.open,
  async (open) => {
    if (open) {
      previousFocus = document.activeElement as HTMLElement
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', onKeydown)
      await nextTick()
      const initial =
        panel.value?.querySelector<HTMLElement>('[autofocus]') ||
        panel.value?.querySelector<HTMLElement>('input, select, textarea, button')
      ;(initial || panel.value)?.focus()
    } else {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', onKeydown)
      previousFocus?.focus()
    }
  },
)

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="ct-modal">
      <div
        v-if="open"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-[2px]"
        @mousedown.self="closeOnBackdrop && close()"
      >
        <section
          ref="panel"
          tabindex="-1"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`${title.replace(/\s+/g, '-')}-title`"
          :aria-describedby="description ? `${title.replace(/\s+/g, '-')}-description` : undefined"
          class="flex max-h-[calc(100vh-2rem)] w-full flex-col overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white shadow-2xl"
          :class="sizes[size]"
        >
          <header
            class="flex items-start justify-between gap-4 border-b border-[var(--ct-border)] bg-slate-50/80 px-5 py-4 sm:px-6"
          >
            <div>
              <h2
                :id="`${title.replace(/\s+/g, '-')}-title`"
                class="text-lg font-semibold text-[var(--ct-ink)]"
              >
                {{ title }}
              </h2>
              <p
                v-if="description"
                :id="`${title.replace(/\s+/g, '-')}-description`"
                class="mt-1 text-sm text-[var(--ct-text-muted)]"
              >
                {{ description }}
              </p>
            </div>
            <button
              type="button"
              aria-label="Fechar janela"
              class="rounded-lg p-2 text-slate-400 hover:bg-white hover:text-slate-700"
              @click="close"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </header>
          <div class="overflow-y-auto"><slot /></div>
          <footer
            v-if="$slots.footer"
            class="border-t border-[var(--ct-border)] bg-slate-50 px-5 py-4 sm:px-6"
          >
            <slot name="footer" />
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.ct-modal-enter-active,
.ct-modal-leave-active {
  transition: opacity 0.18s ease;
}
.ct-modal-enter-from,
.ct-modal-leave-to {
  opacity: 0;
}
</style>
