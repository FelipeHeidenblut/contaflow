import { onBeforeUnmount, onMounted, type Ref } from 'vue'

export const useScrollReveal = (root: Ref<HTMLElement | null>) => {
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    const elements = root.value?.querySelectorAll<HTMLElement>('[data-reveal]') || []
    if (!('IntersectionObserver' in window)) {
      elements.forEach((element) => element.classList.add('is-visible'))
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          entry.target.classList.add('is-visible')
          observer?.unobserve(entry.target)
        })
      },
      { threshold: 0.12 },
    )
    elements.forEach((element) => observer?.observe(element))
  })

  onBeforeUnmount(() => observer?.disconnect())
}
