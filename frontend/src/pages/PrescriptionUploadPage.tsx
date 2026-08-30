import { useState, type ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { confirmPrescription, scanPrescription } from '../api/prescriptions'
import { searchDrugs } from '../api/drugs'
import { useGeolocation } from '../hooks/useGeolocation'
import { ConfidenceTag } from '../components/ConfidenceTag'
import { Disclaimer } from '../components/Disclaimer'
import { PriceBadge } from '../components/PriceBadge'
import { ApiError } from '../api/apiError'
import type { DetectedDrugItem, DrugSearchResult, PrescriptionConfirmResponse } from '../types/api'

interface ResolvedItem extends DetectedDrugItem {
  resolvedDrugId: number | null
  resolvedName: string | null
}

function ManualPicker({ onSelect }: { onSelect: (drug: DrugSearchResult) => void }) {
  const [query, setQuery] = useState('')
  const [options, setOptions] = useState<DrugSearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)

  async function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    setQuery(value)
    if (value.trim().length < 2) {
      setOptions([])
      return
    }
    setIsSearching(true)
    try {
      const results = await searchDrugs(value.trim())
      setOptions(results)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="mt-2">
      <input
        value={query}
        onChange={handleChange}
        placeholder="Qo'lda qidiring..."
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      {isSearching && <p className="mt-1 text-xs text-gray-400">Qidirilmoqda...</p>}
      {options.length > 0 && (
        <ul className="mt-1 divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
          {options.map((option) => (
            <li key={option.id}>
              <button
                type="button"
                onClick={() => {
                  onSelect(option)
                  setOptions([])
                  setQuery(option.trade_name)
                }}
                className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
              >
                {option.trade_name} · {option.substance_name_inn}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function PrescriptionUploadPage() {
  const [status, setStatus] = useState<'idle' | 'scanning' | 'reviewing' | 'confirming' | 'done'>('idle')
  const [items, setItems] = useState<ResolvedItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [confirmResult, setConfirmResult] = useState<PrescriptionConfirmResponse | null>(null)
  const navigate = useNavigate()
  const { coords } = useGeolocation()

  async function handleFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setStatus('scanning')
    setError(null)
    try {
      const res = await scanPrescription(file)
      setItems(
        res.items.map((item) => ({
          ...item,
          resolvedDrugId: item.matched_drug_id,
          resolvedName: item.matched_trade_name,
        })),
      )
      setStatus('reviewing')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Retseptni tahlil qilishda xatolik yuz berdi.')
      setStatus('idle')
    }
  }

  function updateItem(index: number, drugId: number, drugName: string) {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, resolvedDrugId: drugId, resolvedName: drugName } : item)),
    )
  }

  async function handleConfirm() {
    const confirmedItems = items
      .filter((item) => item.resolvedDrugId !== null)
      .map((item) => ({ drug_id: item.resolvedDrugId!, raw_text: item.raw_text }))
    if (confirmedItems.length === 0) return
    setStatus('confirming')
    setError(null)
    try {
      const result = await confirmPrescription(confirmedItems, coords)
      setConfirmResult(result)
      setStatus('done')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Tasdiqlashda xatolik yuz berdi.')
      setStatus('reviewing')
    }
  }

  const resolvedCount = items.filter((item) => item.resolvedDrugId !== null).length

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Retsept yuklash</h1>

      {status === 'idle' && (
        <label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-gray-300 bg-white p-10 text-center hover:border-teal-400">
          <span className="text-3xl">📷</span>
          <span className="font-medium text-gray-700">Rasm tanlang yoki kamerani oching</span>
          <input type="file" accept="image/*" capture="environment" className="hidden" onChange={handleFile} />
        </label>
      )}

      {status === 'scanning' && <p className="text-center text-gray-400">Retsept tahlil qilinmoqda...</p>}

      {error && <p className="rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {status === 'reviewing' && items.length === 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 text-center">
          <p className="text-gray-600">Retseptda hech qanday dori aniqlanmadi.</p>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="mt-3 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700"
          >
            Qo'lda qidirish
          </button>
        </div>
      )}

      {status === 'reviewing' && items.length > 0 && (
        <div className="space-y-4">
          {items.map((item, index) => (
            <div key={index} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium text-gray-900">{item.raw_text}</p>
                <ConfidenceTag status={item.status} />
              </div>
              {item.resolvedDrugId !== null ? (
                <p className="mt-1 text-sm text-teal-700">→ {item.resolvedName}</p>
              ) : (
                <p className="mt-1 text-sm text-red-600">Mos dori topilmadi — qo'lda tanlang</p>
              )}

              {item.status !== 'matched' && item.candidates.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {item.candidates.map((candidate) => (
                    <button
                      key={candidate.drug_id}
                      type="button"
                      onClick={() => updateItem(index, candidate.drug_id, candidate.trade_name)}
                      className={`rounded-lg border px-2.5 py-1 text-xs ${
                        item.resolvedDrugId === candidate.drug_id
                          ? 'border-teal-500 bg-teal-50 text-teal-700'
                          : 'border-gray-200 text-gray-600 hover:border-teal-300'
                      }`}
                    >
                      {candidate.trade_name} ({Math.round(candidate.score)}%)
                    </button>
                  ))}
                </div>
              )}

              {item.status !== 'matched' && (
                <ManualPicker onSelect={(drug) => updateItem(index, drug.id, drug.trade_name)} />
              )}
            </div>
          ))}

          <button
            type="button"
            disabled={resolvedCount === 0}
            onClick={handleConfirm}
            className="w-full rounded-xl bg-teal-600 px-4 py-3 font-medium text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            Tasdiqlash ({resolvedCount}/{items.length})
          </button>
        </div>
      )}

      {status === 'confirming' && <p className="text-center text-gray-400">Narxlar solishtirilmoqda...</p>}

      {status === 'done' && confirmResult && (
        <div className="space-y-6">
          <Disclaimer />
          {confirmResult.results.map((result) => (
            <div key={result.drug.id}>
              <h2 className="mb-2 text-lg font-semibold text-gray-900">{result.drug.trade_name}</h2>
              <div className="space-y-2">
                {result.prices.map((row) => (
                  <div
                    key={row.pharmacy_id}
                    className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-3 shadow-sm"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{row.pharmacy_name}</p>
                      <p className="text-xs text-gray-500">{row.pharmacy_address}</p>
                    </div>
                    <PriceBadge price={row.price} deviationPct={row.deviation_pct} isOverpriced={row.is_overpriced} />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
