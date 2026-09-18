export type TaskStatus = 'pendente' | 'em_andamento' | 'aguardando_cliente' | 'concluida'

export interface Obrigacao {
  id: string | number
  title: string
  description?: string
  status: TaskStatus
  due_date: string
  client_id: string | number
  assigned_to?: string | number | null
  type?: 'custom' | 'receita_federal'
  grau_importancia?: string
  is_recurring?: boolean
  recurrence_day?: number | null
}
