import { request } from './api'
import type { TelegramAuthPayload, TokenResponse, User } from '../types/api'

export function loginWithTelegram(payload: TelegramAuthPayload) {
  return request<TokenResponse>('/auth/telegram', { method: 'POST', body: payload })
}

export function fetchMe() {
  return request<User>('/auth/me')
}
