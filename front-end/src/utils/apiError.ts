type ApiErrorShape = { message?: string; response?: { data?: { detail?: unknown } } }

export const getApiErrorMessage = (error: unknown, fallback: string) => {
  const apiError = error as ApiErrorShape
  const detail = apiError?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== 'object') return ''
        const record = item as Record<string, unknown>
        return typeof record.msg === 'string'
          ? record.msg
          : typeof record.message === 'string'
            ? record.message
            : ''
      })
      .filter(Boolean)
    if (messages.length) return messages.join(' ')
  }
  if (detail && typeof detail === 'object') {
    const message = (detail as Record<string, unknown>).message
    return typeof message === 'string' ? message : fallback
  }
  return apiError?.message && !apiError.message.includes('[object Object]')
    ? apiError.message
    : fallback
}
