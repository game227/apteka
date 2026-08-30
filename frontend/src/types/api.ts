export type UserRole = 'user' | 'pharmacy_staff' | 'admin'

export interface User {
  id: number
  telegram_id: number
  full_name: string
  telegram_username: string | null
  role: UserRole
  pharmacy_id: number | null
}

export interface TelegramAuthPayload {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface DrugSearchResult {
  id: number
  trade_name: string
  substance_name: string
  manufacturer: string
  dosage_form: string
  dosage_strength: string
}

export interface PharmacyPriceEntry {
  pharmacy_id: number
  pharmacy_name: string
  address: string
  lat: number
  lng: number
  distance_km: number | null
  price: number
  in_stock: boolean
  reference_price: number | null
  deviation_percent: number | null
  is_overpriced: boolean
  updated_at: string
}

export interface DrugPricesResponse {
  drug: {
    id: number
    trade_name: string
    substance_name: string
  }
  prices: PharmacyPriceEntry[]
  disclaimer: string
}

export interface DrugAlternative {
  drug_id: number
  trade_name: string
  manufacturer: string
  min_price: number | null
  reference_price: number | null
}

export type ConfidenceLevel = 'high' | 'medium' | 'low'

export interface PrescriptionScanItem {
  raw_text: string
  matched_drug_id: number | null
  matched_trade_name: string | null
  confidence: ConfidenceLevel
  confidence_score: number
}

export interface PrescriptionScanResponse {
  items: PrescriptionScanItem[]
}

export interface PrescriptionConfirmItemResult {
  drug_id: number
  trade_name: string
  prices: PharmacyPriceEntry[]
}

export interface PrescriptionConfirmResponse {
  disclaimer: string
  results: PrescriptionConfirmItemResult[]
}

export interface Pharmacy {
  id: number
  name: string
  address: string
  lat: number
  lng: number
  phone: string
  staff_count?: number
}

export interface PharmacyMyPriceRow {
  drug_id: number
  trade_name: string
  price: number
  in_stock: boolean
  updated_at: string
}

export interface CsvUploadError {
  row: number
  reason: string
}

export interface CsvUploadResult {
  success_count: number
  error_count: number
  errors: CsvUploadError[]
}

export interface PharmacyInviteResponse {
  token: string
  url: string
}
