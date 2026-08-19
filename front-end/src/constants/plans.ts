export type PlanId = 'free' | 'basico' | 'profissional' | 'escritorio' | 'business'
export type BillingCycle = 'monthly' | 'annual'

export interface PlanOption {
  id: PlanId
  name: string
  price: string
  annualPrice: string
  annualMonthlyEquivalent: string
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
    annualPrice: '0',
    annualMonthlyEquivalent: '0',
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
    annualPrice: '799',
    annualMonthlyEquivalent: '66,58',
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
    annualPrice: '1.499',
    annualMonthlyEquivalent: '124,92',
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
    id: 'escritorio',
    name: 'Escritório',
    price: '249,90',
    annualPrice: '2.499',
    annualMonthlyEquivalent: '208,25',
    description: 'Para escritórios consolidados com carteira e equipe maiores.',
    clients: 'Até 300',
    users: 'Até 25',
    features: [
      'Tudo do Profissional',
      'Relatórios avançados de até 12 meses',
      'Desempenho por cliente e colaborador',
      'Filtros avançados e exportação CSV',
    ],
  },
  {
    id: 'business',
    name: 'Empresarial',
    price: '449',
    annualPrice: '4.490',
    annualMonthlyEquivalent: '374,17',
    description: 'Para operações que precisam trabalhar sem limite de equipe ou carteira.',
    clients: 'Ilimitados',
    users: 'Ilimitados',
    features: [
      'Tudo do Escritório',
      'Relatórios avançados de até 12 meses',
      'Desempenho por cliente e colaborador',
      'Filtros avançados e exportação CSV',
    ],
  },
]

export const paidPlanIds: PlanId[] = ['basico', 'profissional', 'escritorio', 'business']

export const isPlanId = (value: unknown): value is PlanId =>
  typeof value === 'string' && plans.some((plan) => plan.id === value)

export const getPlan = (id: unknown) => (isPlanId(id) ? plans.find((plan) => plan.id === id) : null)

export const isBillingCycle = (value: unknown): value is BillingCycle =>
  value === 'monthly' || value === 'annual'

export const getPlanPrice = (plan: PlanOption, cycle: BillingCycle) =>
  cycle === 'annual' ? plan.annualPrice : plan.price

export const getPlanMonthlyPrice = (plan: PlanOption, cycle: BillingCycle) =>
  cycle === 'annual' ? plan.annualMonthlyEquivalent : plan.price
