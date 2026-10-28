<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
const monthOffset = ref(0)
const calendarDate = computed(() => new Date(2026, 9 + monthOffset.value, 1))
const calendarLabel = computed(() =>
  calendarDate.value.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }),
)
const calendarDays = computed(() =>
  Array.from({ length: 42 }, (_, i) => {
    const date = new Date(
      calendarDate.value.getFullYear(),
      calendarDate.value.getMonth(),
      i - calendarDate.value.getDay() + 1,
    )
    return {
      key: i,
      number: date.getDate(),
      current: date.getMonth() === calendarDate.value.getMonth(),
    }
  }),
)
const previewTasks = [
  { name: 'Enviar DCTFWeb', client: 'Comércio Silva', status: 'Em atraso', tone: 'redtag' },
  {
    name: 'Conferir folha de pagamento',
    client: 'Mercado Boa Vista',
    status: 'Em andamento',
    tone: 'bluetag',
  },
  {
    name: 'Enviar EFD-Contribuições',
    client: 'Indústria Lima',
    status: 'Pendente',
    tone: 'yellowtag',
  },
  {
    name: 'Revisar apuração de ICMS',
    client: 'Loja do João',
    status: 'Pendente',
    tone: 'yellowtag',
  },
  {
    name: 'Entregar balancete mensal',
    client: 'Clínica Saúde Mais',
    status: 'Pendente',
    tone: 'yellowtag',
  },
]
const questions = [
  {
    title: 'Como funcionam os 14 dias gratuitos?',
    text: 'Novos escritórios experimentam o Profissional ao concluir o cadastro: até 100 clientes e 10 membros, sem cartão e sem cobrança automática.',
  },
  {
    title: 'O que acontece quando o teste termina?',
    text: 'Sem contratação, sua conta volta ao Gratuito, com 5 clientes ativos e 1 membro. Seus dados permanecem disponíveis. Se estiver acima desses limites, você pode consultar e exportar os dados, adequar a conta ou contratar um plano.',
  },
  {
    title: 'Posso contratar durante o teste?',
    text: 'Sim. A assinatura paga começa após a confirmação do pagamento. Os dias gratuitos restantes não são adicionados à assinatura.',
  },
]
</script>
<template>
  <PublicLayout
    ><div class="reference-landing">
      <svg
        aria-hidden="true"
        style="position: absolute; width: 0; height: 0; overflow: hidden"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <symbol id="landing-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6" /></symbol>
          <symbol id="landing-arrow" viewBox="0 0 24 24"><path d="M4 12h16m-6-6 6 6-6 6" /></symbol>
          <symbol id="landing-calendar" viewBox="0 0 24 24">
            <rect x="3" y="5" width="18" height="16" rx="2" />
            <path d="M7 3v4m10-4v4M3 10h18m-13 5h1m6 0h1" />
          </symbol>
          <symbol id="landing-users" viewBox="0 0 24 24">
            <circle cx="9" cy="7" r="3" />
            <path d="M3 21v-3a6 6 0 0 1 12 0v3m2-18a3 3 0 0 1 0 6m4 12v-3a6 6 0 0 0-4-5" />
          </symbol>
          <symbol id="landing-file" viewBox="0 0 24 24">
            <path d="M14 2H5v20h15V8zM14 2v6h6M8 12h8m-8 4h8" />
          </symbol>
          <symbol id="landing-chart" viewBox="0 0 24 24">
            <path d="M3 21h18M5 17V9h4v8m3 0V4h4v13m3 0V7h2v14" />
          </symbol>
          <symbol id="landing-clock" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v6l3 2" />
          </symbol>
          <symbol id="landing-circle-check" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" />
            <path d="m7 12 3 3 7-7" />
          </symbol>
          <symbol id="landing-play" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" />
            <path d="m10 8 5 4-5 4z" />
          </symbol>
          <symbol id="landing-home" viewBox="0 0 24 24">
            <path d="m3 10 9-7 9 7v11h-6v-8H9v8H3z" />
          </symbol>
          <symbol id="landing-layers" viewBox="0 0 24 24">
            <path d="m12 3 10 5-10 5L2 8zm-10 9 10 5 10-5M2 16l10 5 10-5" />
          </symbol>
          <symbol id="landing-search" viewBox="0 0 24 24">
            <circle cx="10" cy="10" r="6" />
            <path d="m15 15 6 6" />
          </symbol>
          <symbol id="landing-bell" viewBox="0 0 24 24">
            <path d="M5 17h14l-2-4V9a5 5 0 0 0-10 0v4zm5 3h4" />
          </symbol>
          <symbol id="landing-star" viewBox="0 0 24 24">
            <path d="m12 2 3 6 7 1-5 5 1 8-6-4-6 4 1-8-5-5 7-1z" />
          </symbol>
          <symbol id="landing-settings" viewBox="0 0 24 24">
            <path d="m12 2 9 5v10l-9 5-9-5V7z" />
            <circle cx="12" cy="12" r="4" />
          </symbol>
          <symbol id="landing-help" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" />
            <path d="M9 8a3 3 0 0 1 6 1c0 2-3 2-3 5m0 3h.01" />
          </symbol>
        </defs>
      </svg>
      <section class="hero">
        <div class="wrap hero-grid">
          <div>
            <p class="eyebrow">GESTÃO DE TAREFAS PARA ESCRITÓRIOS CONTÁBEIS</p>
            <h1>Organize seu<br />escritório contábil<br />com mais clareza</h1>
            <p class="lead">
              Centralize tarefas, prazos e clientes em um só lugar. Evite atrasos, aumente a
              produtividade da equipe e tenha total visibilidade do que precisa ser feito.
            </p>
            <div class="actions">
              <RouterLink class="btn" to="/cadastro"
                >Começar agora <svg><use href="#landing-arrow" /></svg></RouterLink
              ><RouterLink class="btn outline" to="/como-funciona"
                ><svg style="color: var(--blue)"><use href="#landing-play" /></svg>Ver como
                funciona</RouterLink
              >
            </div>
            <p class="fine">
              14 dias de Profissional grátis <span>•</span> Sem cartão <span>•</span> Sem cobrança
              automática
            </p>
          </div>
          <div class="screen" aria-label="Prévia ilustrativa do painel ContablyTask">
            <aside class="sidebar">
              <div class="brand">
                <span class="brand-mark"
                  ><svg><use href="#landing-check" /></svg></span
                ><span>Contably<em>Task</em></span>
              </div>
              <div class="sideitem active">
                <svg><use href="#landing-home" /></svg>Início
              </div>
              <div class="sideitem">
                <svg><use href="#landing-circle-check" /></svg>Obrigações
              </div>
              <div class="sideitem">
                <svg><use href="#landing-calendar" /></svg>Calendário
              </div>
              <div class="sideitem">
                <svg><use href="#landing-users" /></svg>Clientes
              </div>
              <div class="sideitem">
                <svg><use href="#landing-layers" /></svg>Documentos
              </div>
              <div class="sideitem">
                <svg><use href="#landing-chart" /></svg>Relatórios
              </div>
              <div class="sidebottom">
                <div class="sideitem">
                  <svg><use href="#landing-settings" /></svg>Configurações
                </div>
                <div class="sideitem">
                  <svg><use href="#landing-help" /></svg>Ajuda
                </div>
              </div>
            </aside>
            <div class="screenmain">
              <div class="toolbar">
                <div class="search">
                  <svg><use href="#landing-search" /></svg>Buscar tarefas, clientes ou
                  processos...<span class="key">⌘ K</span>
                </div>
                <svg class="bell"><use href="#landing-bell" /></svg><span class="avatar">AS</span>
              </div>
              <div class="dash">
                <h3>Olá, Ana!</h3>
                <p>Aqui está um resumo das suas tarefas e prazos de hoje.</p>
                <div class="stats">
                  <div class="stat">
                    <span class="round red"
                      ><svg><use href="#landing-clock" /></svg
                    ></span>
                    <div><strong>8</strong><small>Em atraso</small></div>
                  </div>
                  <div class="stat">
                    <span class="round"
                      ><svg><use href="#landing-calendar" /></svg
                    ></span>
                    <div><strong>12</strong><small>Para hoje</small></div>
                  </div>
                  <div class="stat">
                    <span class="round green"
                      ><svg><use href="#landing-circle-check" /></svg
                    ></span>
                    <div>
                      <strong>28</strong><small>Concluídas<br />esta semana</small>
                    </div>
                  </div>
                  <div class="stat">
                    <span class="round purple"
                      ><svg><use href="#landing-users" /></svg
                    ></span>
                    <div><strong>24</strong><small>Clientes ativos</small></div>
                  </div>
                </div>
                <div class="taskbox">
                  <div class="boxhead">
                    Tarefas de hoje<RouterLink to="/cadastro">Ver todas</RouterLink>
                  </div>
                  <div v-for="task in previewTasks" :key="task.name" class="taskrow">
                    <span class="check" aria-hidden="true"></span><span>{{ task.name }}</span
                    ><span class="client">{{ task.client }}</span
                    ><span class="badge" :class="task.tone">{{ task.status }}</span
                    ><span>Hoje</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section id="recursos" class="wrap benefits">
        <article>
          <div class="feature-icon">
            <svg><use href="#landing-calendar" /></svg>
          </div>
          <h3>Controle de prazos</h3>
          <p>Visualize o que precisa ser feito<br />e evite atrasos.</p>
        </article>
        <article>
          <div class="feature-icon">
            <svg><use href="#landing-users" /></svg>
          </div>
          <h3>Organização de clientes</h3>
          <p>Centralize todas as informações<br />dos seus clientes.</p>
        </article>
        <article>
          <div class="feature-icon">
            <svg><use href="#landing-file" /></svg>
          </div>
          <h3>Processos recorrentes</h3>
          <p>Organize e acompanhe<br />tarefas recorrentes.</p>
        </article>
        <article>
          <div class="feature-icon">
            <svg><use href="#landing-chart" /></svg>
          </div>
          <h3>Mais produtividade</h3>
          <p>Tenha visibilidade e acompanhe<br />o progresso da equipe.</p>
        </article>
      </section>
      <section class="overview">
        <div class="wrap">
          <div class="overview-grid">
            <div class="analytics">
              <div class="calendar">
                <h4>Calendário</h4>
                <div class="month">
                  <b>{{ calendarLabel }}</b
                  ><span
                    ><button @click="monthOffset--" type="button" aria-label="Mês anterior">
                      ‹</button
                    ><button @click="monthOffset++" type="button" aria-label="Próximo mês">
                      ›
                    </button></span
                  >
                </div>
                <div class="days">
                  <span
                    v-for="(day, i) in ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']"
                    :key="'w' + i"
                    class="weekday"
                    >{{ day }}</span
                  ><span
                    v-for="day in calendarDays"
                    :key="day.key"
                    class="day"
                    :class="{ muted: !day.current, selected: day.current && day.number === 29 }"
                    >{{ day.number }}</span
                  >
                </div>
              </div>
              <div class="mini-stack">
                <div class="mini-card">
                  <h4>Próximos prazos <a href="/cadastro">Ver todos</a></h4>
                  <div class="due-row">
                    <svg><use href="#landing-calendar" /></svg>Hoje, 29 de out<span
                      class="pill pink"
                      >12</span
                    >
                  </div>
                  <div class="due-row">
                    <svg><use href="#landing-calendar" /></svg>Amanhã, 30 de out<span
                      class="pill yellow"
                      >8</span
                    >
                  </div>
                  <div class="due-row">
                    <svg><use href="#landing-calendar" /></svg>Sábado, 31 de out<span class="pill"
                      >6</span
                    >
                  </div>
                  <div class="due-row">
                    <svg><use href="#landing-calendar" /></svg>Terça, 3 de nov<span class="pill"
                      >10</span
                    >
                  </div>
                </div>
                <div class="mini-card">
                  <h4>Tarefas por status</h4>
                  <div class="chartrow">
                    <div class="donut">
                      <div class="donut-label"><b>48</b>tarefas</div>
                    </div>
                    <div class="legend">
                      <div><i style="background: #ff6870"></i>Em atraso<b>8</b></div>
                      <div><i style="background: #ffce51"></i>Pendentes<b>18</b></div>
                      <div><i style="background: #2185ff"></i>Em andamento<b>12</b></div>
                      <div><i style="background: #16c9a0"></i>Concluídas<b>10</b></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="overview-copy">
              <p class="blue-label">VISÃO GERAL</p>
              <h2>Tudo o que seu escritório precisa, em um só lugar</h2>
              <p class="lead">
                Acompanhe tarefas, prazos, clientes e processos em uma interface simples e
                intuitiva, desenvolvida para a realidade dos escritórios contábeis.
              </p>
              <a class="textlink" href="#recursos"
                >Conheça os recursos <svg><use href="#landing-arrow" /></svg
              ></a>
            </div>
          </div>
          <div class="cta">
            <div>
              <p class="blue-label">PARA ESCRITÓRIOS CONTÁBEIS</p>
              <h2>Menos planilhas.<br />Mais tempo para o que importa.</h2>
              <p class="lead">
                Com a ContablyTask, você ganha organização, segurança e mais tempo para focar nos
                seus clientes.
              </p>
              <RouterLink class="btn" to="/cadastro"
                >Começar agora <svg><use href="#landing-arrow" /></svg
              ></RouterLink>
            </div>
            <div class="checklist">
              <div class="checkline">
                <span class="round"
                  ><svg><use href="#landing-check" /></svg></span
                >Prazos sob controle
              </div>
              <div class="checkline">
                <span class="round"
                  ><svg><use href="#landing-check" /></svg></span
                >Equipe mais produtiva
              </div>
              <div class="checkline">
                <span class="round"
                  ><svg><use href="#landing-check" /></svg></span
                >Processos padronizados
              </div>
            </div>
          </div>
        </div>
      </section>
      <p class="wrap preview-note">Prévia ilustrativa do produto, com dados de exemplo.</p>
      <section class="wrap trust" id="confianca">
        <div>
          <p class="blue-label">COMECE COM CLAREZA</p>
          <h2>Organização para acompanhar o crescimento do seu escritório</h2>
        </div>
        <div class="metrics">
          <div class="metric">
            <svg><use href="#landing-users" /></svg><b>14 dias</b
            ><span>Para testar o Profissional</span>
          </div>
          <div class="metric">
            <svg><use href="#landing-circle-check" /></svg><b>Sem cartão</b
            ><span>Para começar o teste</span>
          </div>
          <div class="metric">
            <svg><use href="#landing-star" /></svg><b>Gratuito</b
            ><span>Plano disponível após o teste</span>
          </div>
        </div>
      </section>
    </div>
    <section class="ct-container grid gap-8 pb-20 lg:grid-cols-[0.8fr_1.2fr]">
      <div>
        <p class="ct-eyebrow">Antes de começar</p>
        <h2 class="ct-section-title mt-4">Um teste sem surpresas.</h2>
        <RouterLink to="/planos" class="mt-5 inline-block text-sm font-semibold text-blue-600"
          >Comparar todos os planos →</RouterLink
        >
      </div>
      <div>
        <details
          v-for="question in questions"
          :key="question.title"
          class="border-b border-slate-200 py-5"
        >
          <summary class="cursor-pointer text-sm font-semibold">{{ question.title }}</summary>
          <p class="mt-3 text-sm leading-7 text-slate-500">{{ question.text }}</p>
        </details>
      </div>
    </section>
  </PublicLayout>
</template>
<style scoped src="../assets/reference-landing.css"></style>
