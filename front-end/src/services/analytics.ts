const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID || 'G-HK0N1KGHBC'
const scriptId = 'contablytask-google-analytics'

type AnalyticsWindow = Window & {
  dataLayer?: unknown[]
  gtag?: (...args: unknown[]) => void
}

let loadingPromise: Promise<void> | null = null

export const loadGoogleAnalytics = (): Promise<void> => {
  if (typeof window === 'undefined' || typeof document === 'undefined') return Promise.resolve()
  if (document.getElementById(scriptId)) return Promise.resolve()
  if (loadingPromise) return loadingPromise

  loadingPromise = new Promise((resolve, reject) => {
    const analyticsWindow = window as AnalyticsWindow
    analyticsWindow.dataLayer = analyticsWindow.dataLayer || []
    analyticsWindow.gtag = (...args: unknown[]) => analyticsWindow.dataLayer?.push(args)
    analyticsWindow.gtag('js', new Date())
    analyticsWindow.gtag('config', measurementId)

    const script = document.createElement('script')
    script.id = scriptId
    script.async = true
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`
    script.onload = () => resolve()
    script.onerror = () => {
      script.remove()
      loadingPromise = null
      reject(new Error('Não foi possível carregar o Google Analytics.'))
    }
    document.head.appendChild(script)
  })

  return loadingPromise
}
