import { ApiError } from '../apiError'
import { getToken } from '../token'
import { drugs, pharmacies, prices, substances } from './mockData'
import type {
  ConfirmedDrugItem,
  CsvRowError,
  CsvUploadResult,
  DrugAlternativesResponse,
  DrugPriceEntry,
  DrugPricesResponse,
  DrugSearchResult,
  Pharmacy,
  PharmacyInviteResponse,
  PharmacyPriceOut,
  PrescriptionScanResponse,
  TelegramAuthPayload,
  TokenResponse,
  User,
} from '../../types/api'

interface MockRequestOptions {
  method?: string
  body?: unknown
  isFormData?: boolean
  query?: Record<string, string | number | undefined>
}

const DISCLAIMER_WARNING =
  "Bu tibbiy maslahat emas, almashtirishdan oldin shifokor yoki farmatsevt bilan maslahatlashing."
const OVERPRICE_THRESHOLD_PERCENT = 20
const TASHKENT_CENTER = { lat: 41.3111, lng: 69.2797 }

const mockPrices = prices.map((p) => ({ ...p }))
const mockPharmacies: Pharmacy[] = pharmacies.map((p) => ({ ...p }))
let nextPharmacyId = mockPharmacies.length + 1
let nextInviteId = 1

interface MockInvite {
  token: string
  pharmacy_id: number
  expires_at: string
  used: boolean
}
const mockInvites: MockInvite[] = []

const mockUsers: User[] = [
  { id: 1, telegram_id: 111, full_name: 'Aziz Karimov', telegram_username: 'aziz_user', role: 'user', pharmacy_id: null },
  { id: 2, telegram_id: 222, full_name: 'Dilnoza Yusupova', telegram_username: 'dilnoza_pharm', role: 'pharmacy_staff', pharmacy_id: 1 },
  { id: 3, telegram_id: 333, full_name: 'Admin Boshqaruvchi', telegram_username: 'apteka_admin', role: 'admin', pharmacy_id: null },
]
let nextUserId = mockUsers.length + 1

const tokenToUserId = new Map<string, number>()

function delay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function haversineKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 6371
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLng = ((lng2 - lng1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function currentUser(): User | null {
  const token = getToken()
  if (!token) return null
  const userId = tokenToUserId.get(token)
  return mockUsers.find((u) => u.id === userId) ?? null
}

function requireAuth(): User {
  const user = currentUser()
  if (!user) throw new ApiError('Bu amal uchun tizimga kirish talab qilinadi.', 401)
  return user
}

function requireRole(role: User['role']): User {
  const user = requireAuth()
  if (user.role !== role) throw new ApiError("Sizda bu sahifaga kirish huquqi yo'q.", 403)
  return user
}

function substanceName(substanceId: number) {
  const substance = substances.find((s) => s.id === substanceId)
  return substance?.name_uz ?? substance?.name_inn ?? ''
}

function normalize(text: string) {
  return text.toLowerCase().trim()
}

function matchesQuery(drug: (typeof drugs)[number], query: string) {
  const q = normalize(query)
  if (normalize(drug.trade_name).includes(q)) return true
  if (drug.aliases.some((alias) => normalize(alias).includes(q))) return true
  return normalize(substanceName(drug.substance_id)).includes(q)
}

function toSearchResult(drug: (typeof drugs)[number]): DrugSearchResult {
  return {
    id: drug.id,
    trade_name: drug.trade_name,
    manufacturer: drug.manufacturer,
    dosage_form: drug.dosage_form,
    dosage_strength: drug.dosage_strength,
    substance_id: drug.substance_id,
    substance_name_inn: substanceName(drug.substance_id),
    reference_price: drug.reference_price,
  }
}

function buildPriceRows(drugId: number, lat: number, lng: number, radiusKm: number) {
  const drug = drugs.find((d) => d.id === drugId)
  if (!drug) throw new ApiError('Dori topilmadi.', 404)

  const rows: DrugPriceEntry[] = mockPrices
    .filter((p) => p.drug_id === drugId)
    .map((p) => {
      const pharmacy = mockPharmacies.find((ph) => ph.id === p.pharmacy_id)
      if (!pharmacy) return null
      const distanceKm = Math.round(haversineKm(lat, lng, pharmacy.lat, pharmacy.lng) * 10) / 10
      const deviationPct = Math.round(((p.price - drug.reference_price) / drug.reference_price) * 100)
      const entry: DrugPriceEntry & { _distance: number } = {
        pharmacy_id: pharmacy.id,
        pharmacy_name: pharmacy.name,
        pharmacy_address: pharmacy.address,
        distance_km: distanceKm,
        price: p.price,
        in_stock: p.in_stock,
        reference_price: drug.reference_price,
        deviation_pct: deviationPct,
        is_overpriced: deviationPct > OVERPRICE_THRESHOLD_PERCENT,
        updated_at: p.updated_at,
        _distance: distanceKm,
      }
      return entry
    })
    .filter((row): row is DrugPriceEntry & { _distance: number } => row !== null && row._distance <= radiusKm)
    .sort((a, b) => a._distance - b._distance)

  return { drug, rows }
}

export async function mockRequest<T>(path: string, options: MockRequestOptions = {}): Promise<T> {
  await delay()

  const method = options.method ?? 'GET'
  const query = options.query ?? {}

  if (path === '/auth/telegram' && method === 'POST') {
    const payload = options.body as TelegramAuthPayload
    let user = mockUsers.find((u) => u.telegram_id === payload.id)
    if (!user) {
      let role: User['role'] = 'user'
      let pharmacyId: number | null = null
      if (payload.invite_token) {
        const invite = mockInvites.find(
          (inv) => inv.token === payload.invite_token && !inv.used && new Date(inv.expires_at) > new Date(),
        )
        if (invite) {
          invite.used = true
          role = 'pharmacy_staff'
          pharmacyId = invite.pharmacy_id
        }
      }
      user = {
        id: nextUserId++,
        telegram_id: payload.id,
        full_name: [payload.first_name, payload.last_name].filter(Boolean).join(' '),
        telegram_username: payload.username ?? null,
        role,
        pharmacy_id: pharmacyId,
      }
      mockUsers.push(user)
    }
    const token = `mock-token-${user.id}-${Date.now()}`
    tokenToUserId.set(token, user.id)
    const response: TokenResponse = { access_token: token, token_type: 'bearer' }
    return response as T
  }

  if (path === '/auth/me' && method === 'GET') {
    return requireAuth() as T
  }

  if (path === '/drugs/search' && method === 'GET') {
    const q = String(query.q ?? '')
    if (!q.trim()) return [] as T
    const results: DrugSearchResult[] = drugs.filter((drug) => matchesQuery(drug, q)).map(toSearchResult)
    return results as T
  }

  const pricesMatch = path.match(/^\/drugs\/(\d+)\/prices$/)
  if (pricesMatch && method === 'GET') {
    const drugId = Number(pricesMatch[1])
    const lat = query.lat !== undefined ? Number(query.lat) : TASHKENT_CENTER.lat
    const lng = query.lng !== undefined ? Number(query.lng) : TASHKENT_CENTER.lng
    const radiusKm = query.radius_km !== undefined ? Number(query.radius_km) : 15
    const { drug, rows } = buildPriceRows(drugId, lat, lng, radiusKm)
    const response: DrugPricesResponse = { drug: toSearchResult(drug), prices: rows }
    return response as T
  }

  const altMatch = path.match(/^\/drugs\/(\d+)\/alternatives$/)
  if (altMatch && method === 'GET') {
    const drugId = Number(altMatch[1])
    const drug = drugs.find((d) => d.id === drugId)
    if (!drug) throw new ApiError('Dori topilmadi.', 404)
    const response: DrugAlternativesResponse = {
      substance_id: drug.substance_id,
      substance_name_inn: substanceName(drug.substance_id),
      alternatives: drugs
        .filter((d) => d.substance_id === drug.substance_id && d.id !== drug.id)
        .map((d) => ({
          id: d.id,
          trade_name: d.trade_name,
          manufacturer: d.manufacturer,
          dosage_form: d.dosage_form,
          dosage_strength: d.dosage_strength,
          reference_price: d.reference_price,
        })),
      warning: DISCLAIMER_WARNING,
    }
    return response as T
  }

  if (path === '/prescriptions/scan' && method === 'POST') {
    await delay(700)
    const [first, second, third] = drugs
    const items: PrescriptionScanResponse['items'] = [
      {
        raw_text: first.trade_name,
        matched_drug_id: first.id,
        matched_trade_name: first.trade_name,
        confidence: 96,
        status: 'matched',
        candidates: [],
      },
      {
        raw_text: second.aliases[0] ?? second.trade_name,
        matched_drug_id: second.id,
        matched_trade_name: second.trade_name,
        confidence: 71,
        status: 'needs_confirmation',
        candidates: [
          { drug_id: second.id, trade_name: second.trade_name, score: 71 },
          { drug_id: third.id, trade_name: third.trade_name, score: 54 },
        ],
      },
      {
        raw_text: "noaniq qo'lyozma...",
        matched_drug_id: null,
        matched_trade_name: null,
        confidence: 22,
        status: 'not_found',
        candidates: [],
      },
    ]
    return { items } as T
  }

  if (path === '/prescriptions/confirm' && method === 'POST') {
    const body = options.body as { items: ConfirmedDrugItem[]; lat?: number | null; lng?: number | null; radius_km?: number }
    const lat = body.lat ?? TASHKENT_CENTER.lat
    const lng = body.lng ?? TASHKENT_CENTER.lng
    const radiusKm = body.radius_km ?? 15
    const results: DrugPricesResponse[] = body.items.map(({ drug_id }) => {
      const { drug, rows } = buildPriceRows(drug_id, lat, lng, radiusKm)
      return { drug: toSearchResult(drug), prices: rows }
    })
    return { results } as T
  }

  if (path === '/pharmacy/my' && method === 'GET') {
    const user = requireRole('pharmacy_staff')
    const pharmacy = mockPharmacies.find((p) => p.id === user.pharmacy_id)
    if (!pharmacy) throw new ApiError('Dorixona topilmadi.', 404)
    return pharmacy as T
  }

  if (path === '/pharmacy/my/prices' && method === 'GET') {
    const user = requireRole('pharmacy_staff')
    const rows: PharmacyPriceOut[] = mockPrices
      .filter((p) => p.pharmacy_id === user.pharmacy_id)
      .map((p) => {
        const drug = drugs.find((d) => d.id === p.drug_id)!
        return { drug_id: p.drug_id, trade_name: drug.trade_name, price: p.price, in_stock: p.in_stock, updated_at: p.updated_at }
      })
      .sort((a, b) => a.trade_name.localeCompare(b.trade_name))
    return rows as T
  }

  if (path === '/pharmacy/my/prices' && method === 'POST') {
    const user = requireRole('pharmacy_staff')
    const body = options.body as { drug_id: number; price: number; in_stock: boolean }
    const drug = drugs.find((d) => d.id === body.drug_id)
    if (!drug) throw new ApiError('Dori topilmadi.', 404)
    const now = new Date().toISOString()
    const existing = mockPrices.find((p) => p.pharmacy_id === user.pharmacy_id && p.drug_id === body.drug_id)
    if (existing) {
      existing.price = body.price
      existing.in_stock = body.in_stock
      existing.updated_at = now
    } else {
      mockPrices.push({ pharmacy_id: user.pharmacy_id!, drug_id: body.drug_id, price: body.price, in_stock: body.in_stock, updated_at: now })
    }
    const row: PharmacyPriceOut = { drug_id: drug.id, trade_name: drug.trade_name, price: body.price, in_stock: body.in_stock, updated_at: now }
    return row as T
  }

  if (path === '/pharmacy/my/prices/csv' && method === 'POST') {
    const user = requireRole('pharmacy_staff')
    const formData = options.body as FormData
    const file = formData.get('file') as File | null
    if (!file) throw new ApiError('Fayl topilmadi.', 400)
    const text = await file.text()
    const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0)
    const hasHeader = lines[0]?.toLowerCase().includes('price') ?? false
    const dataLines = hasHeader ? lines.slice(1) : lines
    const headerOffset = hasHeader ? 1 : 0

    const errors: CsvRowError[] = []
    let imported = 0

    dataLines.forEach((line, index) => {
      const rowNumber = index + 1 + headerOffset
      const columns = line.split(',').map((c) => c.trim())
      const raw = { line: columns.join(',') }
      if (columns.length < 3) {
        errors.push({ row_number: rowNumber, raw, error: 'Ustunlar yetarli emas (trade_name, price, in_stock kerak)' })
        return
      }
      const [nameOrId, priceStr, inStockStr] = columns
      const drug = drugs.find((d) => String(d.id) === nameOrId || normalize(d.trade_name) === normalize(nameOrId))
      if (!drug) {
        errors.push({ row_number: rowNumber, raw, error: `"${nameOrId}" nomli dori bazada topilmadi` })
        return
      }
      const price = Number(priceStr)
      if (!price || price <= 0 || Number.isNaN(price)) {
        errors.push({ row_number: rowNumber, raw, error: `Narx noto'g'ri: "${priceStr}"` })
        return
      }
      const inStock = ['bor', 'true', '1', 'yes'].includes(normalize(inStockStr))
      const now = new Date().toISOString()
      const existing = mockPrices.find((p) => p.pharmacy_id === user.pharmacy_id && p.drug_id === drug.id)
      if (existing) {
        existing.price = price
        existing.in_stock = inStock
        existing.updated_at = now
      } else {
        mockPrices.push({ pharmacy_id: user.pharmacy_id!, drug_id: drug.id, price, in_stock: inStock, updated_at: now })
      }
      imported++
    })

    const result: CsvUploadResult = { imported, errors }
    return result as T
  }

  if (path === '/admin/pharmacies' && method === 'GET') {
    requireRole('admin')
    return mockPharmacies as T
  }

  if (path === '/admin/pharmacies' && method === 'POST') {
    requireRole('admin')
    const body = options.body as { name: string; address: string; lat: number; lng: number; phone: string }
    const pharmacy: Pharmacy = { id: nextPharmacyId++, created_at: new Date().toISOString(), ...body }
    mockPharmacies.push(pharmacy)
    return pharmacy as T
  }

  const inviteMatch = path.match(/^\/admin\/pharmacies\/(\d+)\/invite$/)
  if (inviteMatch && method === 'POST') {
    requireRole('admin')
    const pharmacyId = Number(inviteMatch[1])
    const pharmacy = mockPharmacies.find((p) => p.id === pharmacyId)
    if (!pharmacy) throw new ApiError('Dorixona topilmadi.', 404)
    const token = `invite-${pharmacyId}-${nextInviteId++}`
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    mockInvites.push({ token, pharmacy_id: pharmacyId, expires_at: expiresAt, used: false })
    const response: PharmacyInviteResponse = { token, pharmacy_id: pharmacyId, expires_at: expiresAt }
    return response as T
  }

  throw new ApiError(`Mock endpoint topilmadi: ${method} ${path}`, 404)
}
