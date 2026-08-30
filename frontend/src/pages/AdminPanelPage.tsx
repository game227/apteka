import { useEffect, useState, type FormEvent } from 'react'
import { createPharmacy, createPharmacyInvite, fetchPharmacies } from '../api/admin'
import { ApiError } from '../api/apiError'
import type { Pharmacy } from '../types/api'

export function AdminPanelPage() {
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', address: '', lat: '', lng: '', phone: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [invites, setInvites] = useState<Record<number, string>>({})
  const [copiedId, setCopiedId] = useState<number | null>(null)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setIsLoading(true)
    setError(null)
    try {
      setPharmacies(await fetchPharmacies())
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ro'yxatni yuklashda xatolik yuz berdi.")
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!form.name || !form.address || !form.lat || !form.lng) return
    setIsSubmitting(true)
    setError(null)
    try {
      const created = await createPharmacy({
        name: form.name,
        address: form.address,
        lat: Number(form.lat),
        lng: Number(form.lng),
        phone: form.phone,
      })
      setPharmacies((prev) => [...prev, created])
      setForm({ name: '', address: '', lat: '', lng: '', phone: '' })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Dorixona qo'shishda xatolik yuz berdi.")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleInvite(pharmacyId: number) {
    try {
      const res = await createPharmacyInvite(pharmacyId)
      setInvites((prev) => ({ ...prev, [pharmacyId]: res.url }))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Havola yaratishda xatolik yuz berdi.')
    }
  }

  async function handleCopy(pharmacyId: number, url: string) {
    try {
      await navigator.clipboard.writeText(url)
      setCopiedId(pharmacyId)
      setTimeout(() => setCopiedId(null), 1500)
    } catch {
      // clipboard ruxsati yo'q bo'lsa jim o'tkazamiz
    }
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Admin panel</h1>

      {error && <p className="rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-xl border border-gray-200 bg-white p-4 sm:grid-cols-2">
        <h2 className="font-semibold text-gray-900 sm:col-span-2">Yangi dorixona qo'shish</h2>
        <input
          required
          placeholder="Nomi"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2"
        />
        <input
          required
          placeholder="Telefon"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2"
        />
        <input
          required
          placeholder="Manzil"
          value={form.address}
          onChange={(e) => setForm({ ...form, address: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 sm:col-span-2"
        />
        <input
          required
          placeholder="Latitude"
          value={form.lat}
          onChange={(e) => setForm({ ...form, lat: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2"
        />
        <input
          required
          placeholder="Longitude"
          value={form.lng}
          onChange={(e) => setForm({ ...form, lng: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2"
        />
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-teal-600 px-4 py-2 font-medium text-white hover:bg-teal-700 disabled:bg-gray-300 sm:col-span-2"
        >
          {isSubmitting ? "Qo'shilmoqda..." : "Qo'shish"}
        </button>
      </form>

      {isLoading ? (
        <p className="text-center text-gray-400">Yuklanmoqda...</p>
      ) : (
        <div className="space-y-3">
          {pharmacies.map((pharmacy) => (
            <div key={pharmacy.id} className="rounded-xl border border-gray-200 bg-white p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-gray-900">{pharmacy.name}</p>
                  <p className="text-sm text-gray-500">{pharmacy.address}</p>
                  <p className="text-xs text-gray-400">Xodimlar: {pharmacy.staff_count ?? 0}</p>
                </div>
                <button
                  type="button"
                  onClick={() => handleInvite(pharmacy.id)}
                  className="rounded-lg border border-teal-600 px-3 py-1.5 text-sm font-medium text-teal-700 hover:bg-teal-50"
                >
                  Taklif havolasi yaratish
                </button>
              </div>
              {invites[pharmacy.id] && (
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-gray-50 p-2 text-sm">
                  <code className="flex-1 truncate">{invites[pharmacy.id]}</code>
                  <button
                    type="button"
                    onClick={() => handleCopy(pharmacy.id, invites[pharmacy.id])}
                    className="rounded bg-gray-200 px-2 py-1 text-xs hover:bg-gray-300"
                  >
                    {copiedId === pharmacy.id ? 'Nusxalandi!' : 'Nusxalash'}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
