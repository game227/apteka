import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchDrugAlternatives, fetchDrugPrices } from '../api/drugs'
import { useGeolocation } from '../hooks/useGeolocation'
import { PriceBadge } from '../components/PriceBadge'
import { Disclaimer } from '../components/Disclaimer'
import { ApiError } from '../api/apiError'
import type { DrugAlternative, DrugPricesResponse } from '../types/api'

export function DrugPricesPage() {
  const { drugId } = useParams<{ drugId: string }>()
  const navigate = useNavigate()
  const { coords, isPrecise, isLoading: isLocating } = useGeolocation()
  const [data, setData] = useState<DrugPricesResponse | null>(null)
  const [alternatives, setAlternatives] = useState<DrugAlternative[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!drugId || isLocating) return
    setIsLoading(true)
    setError(null)
    Promise.all([fetchDrugPrices(Number(drugId), coords), fetchDrugAlternatives(Number(drugId))])
      .then(([prices, alts]) => {
        setData(prices)
        setAlternatives(alts)
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'Narxlarni yuklashda xatolik yuz berdi.')
      })
      .finally(() => setIsLoading(false))
  }, [drugId, isLocating, coords.lat, coords.lng])

  if (isLoading || isLocating) {
    return <p className="text-center text-gray-400">Yuklanmoqda...</p>
  }

  if (error) {
    return <p className="rounded-lg bg-red-50 p-4 text-red-700">{error}</p>
  }

  if (!data) return null

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{data.drug.trade_name}</h1>
        <p className="text-sm text-gray-500">{data.drug.substance_name}</p>
        {!isPrecise && (
          <p className="mt-1 text-xs text-gray-400">
            Aniq joylashuv ruxsat etilmadi — shahar markazi bo'yicha ko'rsatilmoqda.
          </p>
        )}
      </div>

      <Disclaimer />

      <div className="space-y-3">
        {data.prices.length === 0 && (
          <p className="text-center text-gray-400">Yaqin atrofda bu dori topilmadi.</p>
        )}
        {data.prices.map((row) => (
          <div key={row.pharmacy_id} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-gray-900">{row.pharmacy_name}</p>
                <p className="text-sm text-gray-500">{row.address}</p>
                <p className="text-xs text-gray-400">
                  {row.distance_km !== null ? `${row.distance_km.toFixed(1)} km` : ''}
                  {!row.in_stock && ' · mavjud emas'}
                </p>
              </div>
              <PriceBadge price={row.price} deviationPercent={row.deviation_percent} isOverpriced={row.is_overpriced} />
            </div>
          </div>
        ))}
      </div>

      {alternatives.length > 0 && (
        <div>
          <h2 className="mb-2 text-lg font-semibold text-gray-900">Shu ta'sir moddali arzonroq variantlar</h2>
          <div className="space-y-2">
            {alternatives.map((alt) => (
              <button
                key={alt.drug_id}
                type="button"
                onClick={() => navigate(`/dori/${alt.drug_id}`)}
                className="flex w-full items-center justify-between rounded-xl border border-gray-200 bg-white p-3 text-left shadow-sm hover:border-teal-300"
              >
                <div>
                  <p className="font-medium text-gray-900">{alt.trade_name}</p>
                  <p className="text-xs text-gray-500">{alt.manufacturer}</p>
                </div>
                {alt.min_price !== null && (
                  <span className="font-semibold text-teal-700">{alt.min_price.toLocaleString('uz-UZ')} so'm dan</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
