import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { fetchMe, loginWithTelegram as apiLoginWithTelegram } from '../api/auth'
import { ApiError } from '../api/apiError'
import { getToken, setToken } from '../api/token'
import type { TelegramAuthPayload, User } from '../types/api'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  error: string | null
  loginWithTelegram: (payload: TelegramAuthPayload, inviteToken?: string | null) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setIsLoading(false)
      return
    }
    fetchMe()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setIsLoading(false))
  }, [])

  async function loginWithTelegram(payload: TelegramAuthPayload, inviteToken?: string | null) {
    setError(null)
    try {
      const res = await apiLoginWithTelegram({ ...payload, invite_token: inviteToken ?? null })
      setToken(res.access_token)
      const me = await fetchMe()
      setUser(me)
    } catch (err) {
      setToken(null)
      setError(err instanceof ApiError ? err.message : 'Kirishda xatolik yuz berdi.')
      throw err
    }
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, error, loginWithTelegram, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth AuthProvider ichida ishlatilishi kerak')
  return ctx
}
