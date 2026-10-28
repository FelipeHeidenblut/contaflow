const siteUrl = 'https://www.contablytask.com.br'
const pages: Record<string, { title: string; description: string }> = {
  '/': {
    title: 'Software de Gestão para Escritórios Contábeis | ContablyTask',
    description:
      'Organize clientes, obrigações, prazos, documentos e equipe do escritório contábil em uma única plataforma. Comece gratuitamente com o ContablyTask.',
  },
  '/como-funciona': {
    title: 'Como Funciona o ContablyTask | Gestão Contábil Organizada',
    description:
      'Veja como o ContablyTask conecta clientes, responsáveis, obrigações, documentos e calendário na rotina do escritório contábil.',
  },
  '/planos': {
    title: 'Planos e Preços para Escritórios Contábeis | ContablyTask',
    description:
      'Conheça os planos Gratuito, Essencial, Profissional, Escritório e Empresarial do ContablyTask, com opções de cobrança mensal e anual.',
  },
  '/sobre': {
    title: 'Sobre o ContablyTask | Organização para Escritórios Contábeis',
    description:
      'Conheça o ContablyTask, plataforma criada para dar clareza, controle e continuidade à operação de escritórios contábeis.',
  },
  '/contato': {
    title: 'Contato | ContablyTask',
    description:
      'Fale com a equipe do ContablyTask sobre planos, demonstrações, suporte técnico ou necessidades do seu escritório contábil.',
  },
  '/privacidade': {
    title: 'Política de Privacidade | ContablyTask',
    description:
      'Entenda como o ContablyTask trata dados pessoais, segurança, armazenamento e direitos dos titulares conforme a LGPD.',
  },
  '/termos': {
    title: 'Termos de Uso | ContablyTask',
    description:
      'Consulte os termos de uso aplicáveis à plataforma ContablyTask e às funcionalidades oferecidas aos escritórios contábeis.',
  },
}

export function updatePageSeo(path: string, fallbackTitle?: string) {
  const normalized = path === '/' ? '/' : path.replace(/\/$/, '')
  const page = pages[normalized]
  const title = page?.title ?? `${fallbackTitle || 'ContablyTask'} · ContablyTask`
  const description =
    page?.description ?? 'Acesse sua conta ContablyTask para organizar a rotina do seu escritório.'
  document.title = title
  function meta(selector: string, content: string) {
    document.querySelector(selector)?.setAttribute('content', content)
  }
  meta('meta[name="description"]', description)
  meta(
    'meta[name="robots"]',
    page
      ? 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1'
      : 'noindex, nofollow',
  )
  meta('meta[property="og:title"]', title)
  meta('meta[property="og:description"]', description)
  meta('meta[name="twitter:title"]', title)
  meta('meta[name="twitter:description"]', description)
  const url = `${siteUrl}${normalized}`
  meta('meta[property="og:url"]', url)
  let canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (page) {
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    canonical.href = url
  } else {
    canonical?.remove()
  }
}
