import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { TelegramLoginButton } from '../components/TelegramLoginButton'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) navigate('/', { replace: true })
  }, [user, navigate])

  return (
    <div className="mx-auto max-w-sm space-y-4 text-center">
      <h1 className="text-2xl font-bold text-gray-900">Kirish</h1>
      <p className="text-sm text-gray-500">
        Narx tarixini ko'rish, dorixona yoki admin panelga kirish uchun Telegram orqali tizimga kiring.
      </p>
      <TelegramLoginButton />
    </div>
  )
}
