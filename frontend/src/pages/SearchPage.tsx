import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { DrugSearchInput } from '../components/DrugSearchInput'
import { searchDrugs } from '../api/drugs'
import { ApiError } from '../api/apiError'
import type { DrugSearchResult } from '../types/api'

export function SearchPage() {
  const [results, setResults] = useState<DrugSearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const navigate = useNavigate()

  const handleSearch = useCallback(async (query: string) => {
    if (!query) {
      setResults([])
      setHasSearched(false)
      return
    }
    setIsLoading(true)
    setError(null)
    setHasSearched(true)
    try {
      const data = await searchDrugs(query)
      setResults(data)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Qidirishda xatolik yuz berdi.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Dori qidirish</h1>
      <DrugSearchInput onSearch={handleSearch} autoFocus />

      <button
        type="button"
        onClick={() => navigate('/retsept')}
        className="mt-3 w-full rounded-xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm font-medium text-teal-700 hover:bg-teal-100"
      >
        📷 Retsept yuklash
      </button>

      <div className="mt-6 space-y-3">
        {isLoading && <p className="text-center text-gray-400">Qidirilmoqda...</p>}
        {error && <p className="rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}
        {!isLoading && hasSearched && !error && results.length === 0 && (
          <p className="text-center text-gray-400">Hech narsa topilmadi.</p>
        )}
        {results.map((drug) => (
          <div
            key={drug.id}
            className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div>
              <p className="font-semibold text-gray-900">{drug.trade_name}</p>
              <p className="text-sm text-gray-500">
                {drug.substance_name_inn} · {drug.dosage_form} {drug.dosage_strength}
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate(`/dori/${drug.id}`)}
              className="rounded-lg bg-teal-600 px-3 py-2 text-sm font-medium text-white hover:bg-teal-700"
            >
              Narxlarni ko'rish
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
