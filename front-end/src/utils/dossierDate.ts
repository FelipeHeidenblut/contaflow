const documentDateFormatter = new Intl.DateTimeFormat('pt-BR', {
  timeZone: 'America/Sao_Paulo',
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

export const formatDossierDate = (value: string | null | undefined): string => {
  if (!value) return '-'
  const calendarDate = value.slice(0, 10)
  const calendarDay = new Date(`${calendarDate}T12:00:00Z`)
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(calendarDate) ||
    Number.isNaN(calendarDay.getTime()) ||
    calendarDay.toISOString().slice(0, 10) !== calendarDate
  )
    return '-'

  // Prazos são datas de calendário, sem conversão de fuso.
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-')
    return `${day}/${month}/${year}`
  }

  // Envios são instantes ISO; valores sem fuso não devem ser interpretados
  // segundo o fuso do computador de quem abre o dossiê.
  if (!/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/i.test(value)) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '-' : documentDateFormatter.format(date)
}
