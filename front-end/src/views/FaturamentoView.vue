<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

const isLoadingPlano = ref<string | null>(null)

const planos = [
  {
    nome: 'Free',
    price: '0',
    desc: 'Para testar a plataforma.',
    cta: 'Plano Atual',
    isFree: true, // Flag para não chamar o Asaas
    features: [
      'Até 5 clientes',
      '1 usuário (Admin)',
      'Calendário de obrigações',
      'Gestão de documentos',
      'Suporte por e-mail',
    ],
  },
  {
    nome: 'Básico',
    price: '149',
    desc: 'Para contadores autônomos.',
    cta: 'Assinar Básico',
    features: [
      'Até 40 clientes',
      'Até 5 usuários',
      'Tudo do Free',
      'Alertas por e-mail',
      'Suporte por chat',
    ],
  },
  {
    nome: 'Profissional',
    price: '197',
    featured: true,
    desc: 'Para escritórios em crescimento.',
    cta: 'Assinar Profissional',
    features: [
      'Até 100 clientes',
      'Até 10 usuários',
      'Tudo do Básico',
      'Distribuição de equipe',
      'Relatórios avançados',
      'Suporte prioritário',
    ],
  },
  {
    nome: 'Business',
    price: '449',
    desc: 'Para grandes operações.',
    cta: 'Falar com vendas',
    features: [
      'Clientes ilimitados',
      'Usuários ilimitados',
      'Tudo do Profissional',
      'API e integrações',
      'Gerente de conta dedicado',
      'Onboarding assistido',
    ],
  },
]

const assinarPlano = async (nomePlano: string, isFree: boolean = false) => {
  // Se o usuário tentar "assinar" o plano free, apenas avisa
  if (isFree) {
    toast.info('Você já pode utilizar os recursos do plano Free. Faça upgrade para liberar mais!')
    return
  }

  isLoadingPlano.value = nomePlano
  try {
    // NORMALIZAÇÃO: Remove acentos e passa para minúsculo (Ex: "Básico" -> "basico")
    const planoFormatado = nomePlano
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()

    // Chama o backend com o nome formatado
    const response = await api.post(`/api/v1/asaas/criar-assinatura/${planoFormatado}`)

    // Validação estrita para evitar falhas silenciosas
    if (response.data.invoice_url) {
      toast.success('Estamos te redirecionando para o pagamento seguro...')

      // Utiliza location.href para evitar bloqueadores de pop-up no navegador do cliente
      window.location.href = response.data.invoice_url
    } else {
      toast.error('Assinatura criada, mas o link de pagamento ainda está sendo gerado.')
    }
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao gerar a cobrança do plano.'
    toast.error(detail)
  } finally {
    isLoadingPlano.value = null
  }
}
</script>

<template>
  <Layout title="Planos e Faturamento">
    <header class="mb-8 text-center">
      <h1 class="text-3xl font-extrabold text-[#19341a] tracking-tight">
        Escolha o plano ideal para o seu escritório
      </h1>
      <p class="text-gray-500 mt-2">
        Cancele quando quiser. Sem fidelidade. Pague com PIX, Boleto ou Cartão.
      </p>
    </header>

    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 items-start">
      <div
        v-for="plano in planos"
        :key="plano.nome"
        class="bg-white border rounded-2xl p-8 relative transition-all duration-300 hover:shadow-lg"
        :class="
          plano.featured
            ? 'border-[#ff8a65] shadow-[0_20px_50px_rgba(25,52,26,0.1)] md:scale-105 z-10'
            : 'border-gray-100'
        "
      >
        <div
          v-if="plano.featured"
          class="absolute top-[-14px] left-1/2 -translate-x-1/2 bg-[#ff8a65] text-white rounded-full py-1.5 px-5 text-[0.75rem] font-bold whitespace-nowrap shadow-md"
        >
          Mais popular
        </div>

        <div class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-3">
          {{ plano.nome }}
        </div>

        <div class="flex items-end gap-1 mb-1">
          <span class="text-2xl font-bold text-gray-400 mb-1">R$</span>
          <span class="text-4xl font-extrabold text-[#19341a] leading-none">{{ plano.price }}</span>
        </div>
        <div class="text-sm text-gray-400 font-medium mb-6">/mês</div>

        <div class="text-sm text-gray-500 mt-2 mb-6 min-h-[40px]">{{ plano.desc }}</div>

        <ul class="mb-8 space-y-3 border-t border-gray-100 pt-6">
          <li
            v-for="f in plano.features"
            :key="f"
            class="text-sm text-[#2a2a2a] flex items-start gap-2.5"
          >
            <svg
              class="w-4 h-4 text-[#ff8a65] mt-0.5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="3"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
            {{ f }}
          </li>
        </ul>

        <button
          @click="assinarPlano(plano.nome, plano.isFree)"
          :disabled="isLoadingPlano === plano.nome || plano.isFree"
          class="w-full rounded-xl py-3 font-bold text-sm cursor-pointer transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="
            plano.featured
              ? 'bg-[#ff8a65] text-white hover:bg-[#f07047] shadow-lg shadow-[#ff8a65]/30'
              : 'bg-transparent text-[#19341a] border-2 border-gray-200 hover:border-[#19341a] hover:bg-white'
          "
        >
          {{ isLoadingPlano === plano.nome ? 'Gerando cobrança...' : plano.cta }}
        </button>
      </div>
    </div>
  </Layout>
</template>
