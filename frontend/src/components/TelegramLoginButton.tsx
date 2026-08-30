import { useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import type { TelegramAuthPayload } from '../types/api'

const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true'
const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME as string | undefined

declare global {
  interface Window {
    onTelegramAuth?: (user: TelegramAuthPayload) => void
  }
}

const MOCK_ACCOUNTS: { label: string; payload: TelegramAuthPayload }[] = [
  { label: 'Foydalanuvchi sifatida', payload: { id: 111, first_name: 'Aziz', username: 'aziz_user', auth_date: Math.floor(Date.now() / 1000), hash: 'mock' } },
  { label: 'Dorixona xodimi sifatida', payload: { id: 222, first_name: 'Dilnoza', username: 'dilnoza_pharm', auth_date: Math.floor(Date.now() / 1000), hash: 'mock' } },
  { label: 'Admin sifatida', payload: { id: 333, first_name: 'Admin', username: 'apteka_admin', auth_date: Math.floor(Date.now() / 1000), hash: 'mock' } },
]

export function TelegramLoginButton() {
  const { loginWithTelegram } = useAuth()
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (USE_MOCK || !BOT_USERNAME) return

    window.onTelegramAuth = (user) => {
      loginWithTelegram(user).catch(() => {})
    }

    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.async = true
    script.setAttribute('data-telegram-login', BOT_USERNAME)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', 'write')
    containerRef.current?.appendChild(script)

    return () => {
      window.onTelegramAuth = undefined
    }
  }, [loginWithTelegram])

  if (USE_MOCK || !BOT_USERNAME) {
    return (
      <div className="flex flex-col gap-2 rounded-xl border border-dashed border-gray-300 p-4">
        <p className="text-sm text-gray-500">
          Mock rejim: Telegram Login Widget o'rniga test hisoblari bilan kiring.
        </p>
        {MOCK_ACCOUNTS.map((account) => (
          <button
            key={account.payload.id}
            type="button"
            onClick={() => loginWithTelegram(account.payload)}
            className="rounded-lg bg-[#2AABEE] px-4 py-2 text-sm font-medium text-white hover:bg-[#2596d1]"
          >
            {account.label}
          </button>
        ))}
      </div>
    )
  }

  return <div ref={containerRef} />
}
