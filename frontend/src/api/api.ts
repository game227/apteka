import { ApiError } from './apiError'
import { mockRequest } from './mock/mockServer'
import { getToken } from './token'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true'

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  isFormData?: boolean
  query?: Record<string, string | number | undefined>
}

function buildUrl(path: string, query?: RequestOptions['query']) {
  const url = new URL(path, API_BASE_URL)
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null) url.searchParams.set(key, String(value))
    }
  }
  return url.toString()
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  if (USE_MOCK) {
    return mockRequest<T>(path, options)
  }

  const headers: Record<string, string> = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let body: BodyInit | undefined
  if (options.body !== undefined) {
    if (options.isFormData) {
      body = options.body as FormData
    } else {
      headers['Content-Type'] = 'application/json'
      body = JSON.stringify(options.body)
    }
  }

  let response: Response
  try {
    response = await fetch(buildUrl(path, options.query), {
      method: options.method ?? 'GET',
      headers,
      body,
    })
  } catch {
    throw new ApiError("Serverga ulanib bo'lmadi. Internet aloqasini tekshiring.")
  }

  if (!response.ok) {
    let message = "Noma'lum xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."
    try {
      const data = await response.json()
      if (typeof data?.detail === 'string') message = data.detail
      else if (typeof data?.message === 'string') message = data.message
    } catch {
      // javob JSON emas — standart xabar qoladi
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}
