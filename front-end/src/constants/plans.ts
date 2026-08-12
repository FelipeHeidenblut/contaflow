export type PlanId = 'free' | 'basico' | 'profissional' | 'business'

export interface PlanOption {
  id: PlanId
  name: string
  price: string
  description: string
  clients: string
  users: string
  features: string[]
  featured?: boolean
  sales?: boolean
}

export const plans: PlanOption[] = [
  {
    id: 'free',
    name: 'Gratuito',
    price: '0',
    description: 'Para experimentar a rotina com uma carteira pequena.',
    clients: 'Até 5',
    users: '1 administrador',
    features: [
      'Obrigações, calendário e documentos',
      'Responsáveis e prioridades',
      'Visão operacional do dashboard',
    ],
  },
  {
    id: 'basico',
    name: 'Essencial',
    price: '79,90',
    description: 'Para contadores autônomos e equipes em formação.',
    clients: 'Até 40',
    users: 'Até 5',
    features: [
      'Obrigações, calendário e documentos',
      'Responsáveis e prioridades',
      'Resumo operacional de até 3 meses',
      'Indicadores de entregas e atrasos',
    ],
  },
  {
    id: 'profissional',
    name: 'Profissional',
    price: '149,90',
    description: 'Para gerenciar produtividade, gargalos e uma carteira em crescimento.',
    clients: 'Até 100',
    users: 'Até 10',
    features: [
      'Tudo do Essencial',
      'Relatórios avançados de até 12 meses',
      'Desempenho por cliente e colaborador',
      'Filtros avançados e exportação CSV',
    ],
    featured: true,
  },
  {
    id: 'business',
    name: 'Empresarial',
    price: '449',
    description: 'Para operações que precisam trabalhar sem limite de equipe ou carteira.',
    clients: 'Ilimitados',
    users: 'Ilimitados',
    features: [
      'Tudo do Profissional',
      'Relatórios avançados de até 12 meses',
      'Desempenho por cliente e colaborador',
      'Filtros avançados e exportação CSV',
    ],
    sales: true,
  },
]

export const paidPlanIds: PlanId[] = ['basico', 'profissional', 'business']

export const isPlanId = (value: unknown): value is PlanId =>
  typeof value === 'string' && plans.some((plan) => plan.id === value)

export const getPlan = (id: unknown) => (isPlanId(id) ? plans.find((plan) => plan.id === id) : null)
