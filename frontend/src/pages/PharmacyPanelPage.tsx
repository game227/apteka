import { useEffect, useState, type ChangeEvent } from 'react'
import { fetchMyPharmacy, fetchMyPharmacyPrices, upsertMyPrice, uploadPricesCsv } from '../api/pharmacy'
import { ApiError } from '../api/apiError'
import type { CsvUploadResult, Pharmacy, PharmacyPriceOut } from '../types/api'

export function PharmacyPanelPage() {
  const [pharmacy, setPharmacy] = useState<Pharmacy | null>(null)
  const [rows, setRows] = useState<PharmacyPriceOut[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editPrice, setEditPrice] = useState('')
  const [editInStock, setEditInStock] = useState(true)
  const [csvResult, setCsvResult] = useState<CsvUploadResult | null>(null)
  const [isUploadingCsv, setIsUploadingCsv] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setIsLoading(true)
    setError(null)
    try {
      const [pharmacyData, priceRows] = await Promise.all([fetchMyPharmacy(), fetchMyPharmacyPrices()])
      setPharmacy(pharmacyData)
      setRows(priceRows)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ma'lumotlarni yuklashda xatolik yuz berdi.")
    } finally {
      setIsLoading(false)
    }
  }

  function startEdit(row: PharmacyPriceOut) {
    setEditingId(row.drug_id)
    setEditPrice(String(row.price))
    setEditInStock(row.in_stock)
  }

  async function saveEdit(drugId: number) {
    const price = Number(editPrice)
    if (!price || price <= 0) return
    try {
      const updated = await upsertMyPrice({ drug_id: drugId, price, in_stock: editInStock })
      setRows((prev) => prev.map((row) => (row.drug_id === drugId ? updated : row)))
      setEditingId(null)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Saqlashda xatolik yuz berdi.')
    }
  }

  async function handleCsv(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploadingCsv(true)
    setCsvResult(null)
    setError(null)
    try {
      const result = await uploadPricesCsv(file)
      setCsvResult(result)
      await loadData()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'CSV yuklashda xatolik yuz berdi.')
    } finally {
      setIsUploadingCsv(false)
      e.target.value = ''
    }
  }

  if (isLoading) return <p className="text-center text-gray-400">Yuklanmoqda...</p>

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{pharmacy?.name}</h1>
          <p className="text-sm text-gray-500">{pharmacy?.address}</p>
        </div>
        <label className="cursor-pointer rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700">
          {isUploadingCsv ? 'Yuklanmoqda...' : 'CSV yuklash'}
          <input type="file" accept=".csv" className="hidden" onChange={handleCsv} disabled={isUploadingCsv} />
        </label>
      </div>

      {error && <p className="rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {csvResult && (
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="font-medium text-gray-900">
            {csvResult.imported} ta qator muvaffaqiyatli, {csvResult.errors.length} ta xato
          </p>
          {csvResult.errors.length > 0 && (
            <ul className="mt-2 space-y-1 text-sm text-red-700">
              {csvResult.errors.map((err) => (
                <li key={err.row_number}>
                  {err.row_number}-qator: {err.error}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-500">
            <tr>
              <th className="px-4 py-2">Dori</th>
              <th className="px-4 py-2">Narx</th>
              <th className="px-4 py-2">Mavjudligi</th>
              <th className="px-4 py-2">Yangilangan</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {rows.map((row) => (
              <tr
                key={row.drug_id}
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => editingId !== row.drug_id && startEdit(row)}
              >
                <td className="px-4 py-2 font-medium text-gray-900">{row.trade_name}</td>
                {editingId === row.drug_id ? (
                  <>
                    <td className="px-4 py-2" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="number"
                        value={editPrice}
                        onChange={(e) => setEditPrice(e.target.value)}
                        className="w-24 rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="px-4 py-2" onClick={(e) => e.stopPropagation()}>
                      <select
                        value={editInStock ? 'bor' : 'yoq'}
                        onChange={(e) => setEditInStock(e.target.value === 'bor')}
                        className="rounded border border-gray-300 px-2 py-1"
                      >
                        <option value="bor">Bor</option>
                        <option value="yoq">Yo'q</option>
                      </select>
                    </td>
                    <td className="px-4 py-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => saveEdit(row.drug_id)}
                        className="rounded bg-teal-600 px-3 py-1 text-white"
                      >
                        Saqlash
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="px-4 py-2">{row.price.toLocaleString('uz-UZ')} so'm</td>
                    <td className="px-4 py-2">{row.in_stock ? 'Bor' : "Yo'q"}</td>
                    <td className="px-4 py-2 text-gray-400">{new Date(row.updated_at).toLocaleString('uz-UZ')}</td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
