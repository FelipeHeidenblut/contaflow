import api from './api'

export interface PaginatedResponse<T> {
  items: T[]
  page: number
  page_size: number
  total: number
  pages: number
  summary: Record<string, number> | null
}

const MAX_PAGE_SIZE = 100

export const fetchPage = async <T>(
  url: string,
  page: number,
  pageSize: number,
  params: Record<string, string | number | boolean | null | undefined> = {},
): Promise<PaginatedResponse<T>> => {
  const { data } = await api.get<PaginatedResponse<T>>(url, {
    params: { ...params, page, page_size: pageSize },
  })
  return data
}

export const fetchAllPages = async <T>(
  url: string,
  params: Record<string, string | number | boolean | null | undefined> = {},
): Promise<T[]> => {
  const items: T[] = []
  let page = 1
  let totalPages = 1

  while (page <= totalPages) {
    const { data } = await api.get<PaginatedResponse<T>>(url, {
      params: { ...params, page, page_size: MAX_PAGE_SIZE },
    })
    items.push(...data.items)
    totalPages = data.pages
    page += 1
  }

  return items
}
