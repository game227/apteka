import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <Link to="/" className="text-lg font-bold text-teal-700">
            Dori Narxlari
          </Link>
          <nav className="flex flex-wrap items-center gap-4 text-sm">
            <Link to="/" className="text-gray-600 hover:text-teal-700">Qidiruv</Link>
            <Link to="/retsept" className="text-gray-600 hover:text-teal-700">Retsept yuklash</Link>
            {user?.role === 'pharmacy_staff' && (
              <Link to="/dorixona" className="text-gray-600 hover:text-teal-700">Dorixona paneli</Link>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin" className="text-gray-600 hover:text-teal-700">Admin panel</Link>
            )}
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-gray-500">{user.full_name}</span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-lg border border-gray-300 px-3 py-1.5 hover:bg-gray-100"
                >
                  Chiqish
                </button>
              </div>
            ) : (
              <Link to="/kirish" className="rounded-lg bg-teal-600 px-3 py-1.5 text-white hover:bg-teal-700">
                Kirish
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
    </div>
  )
}
