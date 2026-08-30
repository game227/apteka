import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { TelegramLoginButton } from '../components/TelegramLoginButton'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const inviteToken = searchParams.get('invite')

  useEffect(() => {
    if (user) navigate('/', { replace: true })
  }, [user, navigate])

  return (
    <div className="mx-auto max-w-sm space-y-4 text-center">
      <h1 className="text-2xl font-bold text-gray-900">Kirish</h1>
      <p className="text-sm text-gray-500">
        Narx tarixini ko'rish, dorixona yoki admin panelga kirish uchun Telegram orqali tizimga kiring.
      </p>
      {inviteToken && (
        <p className="rounded-lg bg-teal-50 p-3 text-sm text-teal-700">
          Dorixona xodimi sifatida taklif havolasi orqali kirmoqdasiz.
        </p>
      )}
      <TelegramLoginButton inviteToken={inviteToken} />
    </div>
  )
}
