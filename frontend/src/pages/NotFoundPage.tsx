import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="py-16 text-center">
      <p className="text-lg text-gray-600">Sahifa topilmadi.</p>
      <Link to="/" className="mt-3 inline-block text-teal-700 underline">
        Bosh sahifaga qaytish
      </Link>
    </div>
  )
}
