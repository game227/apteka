import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { UserRole } from '../types/api'

interface RoleGuardProps {
  allow: UserRole[]
  children: ReactNode
}

export function RoleGuard({ allow, children }: RoleGuardProps) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Yuklanmoqda...</div>
  }

  if (!user || !allow.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
