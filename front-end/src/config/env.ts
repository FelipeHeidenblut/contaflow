export type AppEnvironment = 'development' | 'test' | 'staging' | 'production'

const environments = new Set<AppEnvironment>(['development', 'test', 'staging', 'production'])

const required = (name: keyof ImportMetaEnv): string => {
  const value = import.meta.env[name]?.trim()
  if (!value) throw new Error(`Configuração obrigatória ausente: ${name}`)
  return value
}

const normalizeUrl = (name: keyof ImportMetaEnv): string => {
  const value = required(name).replace(/\/$/, '')
  try {
    const url = new URL(value)
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error()
  } catch {
    throw new Error(`URL inválida em ${name}`)
  }
  return value
}

const configuredEnvironment = required('VITE_APP_ENV') as AppEnvironment

if (!environments.has(configuredEnvironment)) {
  throw new Error('VITE_APP_ENV deve ser development, test, staging ou production.')
}

const apiBaseUrl = normalizeUrl('VITE_API_URL')
const turnstileSiteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY?.trim() || ''
if (['staging', 'production'].includes(configuredEnvironment)) {
  const apiHostname = new URL(apiBaseUrl).hostname
  if (['localhost', '127.0.0.1', '[::1]'].includes(apiHostname)) {
    throw new Error(`API local não permitida no ambiente ${configuredEnvironment}.`)
  }
  if (!turnstileSiteKey) {
    throw new Error(`VITE_TURNSTILE_SITE_KEY é obrigatória no ambiente ${configuredEnvironment}.`)
  }
}

export const appConfig = Object.freeze({
  environment: configuredEnvironment,
  apiBaseUrl,
  supabaseUrl: normalizeUrl('VITE_SUPABASE_URL'),
  supabaseAnonKey: required('VITE_SUPABASE_ANON_KEY'),
  turnstileSiteKey,
  gaMeasurementId: import.meta.env.VITE_GA_MEASUREMENT_ID?.trim() || '',
})
