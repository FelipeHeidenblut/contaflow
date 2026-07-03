<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import AdminLayout from '../components/AdminLayout.vue'
import { toast } from 'vue3-toastify'

// Tipagem rigorosa para evitar erros de runtime
interface SaasStats {
  mrr_estimado: number
  total_escritorios: number
  escritorios_ativos: number
  escritorios_inadimplentes: number
  total_usuarios: number
  total_clientes_finais: number
}

const stats = ref<SaasStats | null>(null)
const isLoading = ref(true)

const fetchStats = async () => {
  try {
    const response = await api.get<SaasStats>('/api/v1/admin/dashboard-stats')
    stats.value = response.data
  } catch (error: any) {
    if (error.response?.status === 403) {
      toast.error('Você não tem permissão para acessar esta área.')
    } else {
      toast.error('Erro ao carregar as métricas do SaaS.')
    }
  } finally {
    isLoading.value = false
  }
}

// Formatador utilitário para moeda (BRL)
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <AdminLayout title="Backoffice SaaS">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-[#19341a] tracking-tight">Visão Global do Negócio</h1>
      <p class="text-gray-500 mt-1">Métricas de faturamento e adoção em tempo real.</p>
    </div>

    <!-- Skeleton Loading Elegante -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="i in 4"
        :key="i"
        class="bg-white border border-gray-100 rounded-2xl p-6 h-32 animate-pulse"
      >
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="h-8 bg-gray-300 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Cards de KPIs (Key Performance Indicators) -->
    <div v-else-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Card MRR -->
      <div
        class="bg-white border-l-4 border-[#ff8a65] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">MRR Estimado</h3>
        <p class="text-3xl font-extrabold text-[#19341a]">
          {{ formatCurrency(stats.mrr_estimado) }}
        </p>
        <p class="text-xs text-gray-400 mt-2">Receita recorrente de planos ativos</p>
      </div>

      <!-- Card Escritórios -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Escritórios Ativos
        </h3>
        <div class="flex items-end gap-2">
          <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.escritorios_ativos }}</p>
          <p class="text-sm font-medium text-gray-400 mb-1">
            / {{ stats.total_escritorios }} total
          </p>
        </div>
        <p class="text-xs text-red-500 mt-2 font-medium" v-if="stats.escritorios_inadimplentes > 0">
          {{ stats.escritorios_inadimplentes }} inadimplentes
        </p>
        <p class="text-xs text-green-500 mt-2 font-medium" v-else>Inadimplência zero 🎉</p>
      </div>

      <!-- Card Usuários -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Usuários (Profiles)
        </h3>
        <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.total_usuarios }}</p>
        <p class="text-xs text-gray-400 mt-2">Pessoas acessando o sistema</p>
      </div>

      <!-- Card Volume de Dados -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Clientes Finais
        </h3>
        <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.total_clientes_finais }}</p>
        <p class="text-xs text-gray-400 mt-2">Empresas gerenciadas na plataforma</p>
      </div>
    </div>
  </AdminLayout>
</template>
