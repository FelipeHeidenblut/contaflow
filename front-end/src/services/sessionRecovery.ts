// A primeira consulta autenticada pode precisar aguardar a inicialização da API.
export const SESSION_REQUEST_TIMEOUT_MS = 90_000

export const isTemporarySessionError = (error: unknown): boolean => {
  const candidate = error as { code?: string; response?: { status?: number } } | null
  return (
    ['ECONNABORTED', 'ETIMEDOUT', 'ERR_NETWORK'].includes(candidate?.code || '') ||
    [408, 429, 502, 503, 504].includes(candidate?.response?.status || 0)
  )
}
