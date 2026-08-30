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
  first_name?: string | null
  last_name?: string | null
  username?: string | null
  photo_url?: string | null
  auth_date: number
  hash: string
  invite_token?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface DrugSearchResult {
  id: number
  trade_name: string
  manufacturer: string | null
  dosage_form: string | null
  dosage_strength: string | null
  substance_id: number
  substance_name_inn: string
  reference_price: number | null
}

export interface DrugPriceEntry {
  pharmacy_id: number
  pharmacy_name: string
  pharmacy_address: string
  distance_km: number | null
  price: number
  in_stock: boolean
  reference_price: number | null
  deviation_pct: number | null
  is_overpriced: boolean
  updated_at: string
}

export interface DrugPricesResponse {
  drug: DrugSearchResult
  prices: DrugPriceEntry[]
}

export interface DrugAlternative {
  id: number
  trade_name: string
  manufacturer: string | null
  dosage_form: string | null
  dosage_strength: string | null
  reference_price: number | null
}

export interface DrugAlternativesResponse {
  substance_id: number
  substance_name_inn: string
  alternatives: DrugAlternative[]
  warning?: string
}

export type PrescriptionItemStatus = 'matched' | 'needs_confirmation' | 'not_found'

export interface MatchCandidate {
  drug_id: number
  trade_name: string
  score: number
}

export interface DetectedDrugItem {
  raw_text: string
  matched_drug_id: number | null
  matched_trade_name: string | null
  confidence: number
  status: PrescriptionItemStatus
  candidates: MatchCandidate[]
}

export interface PrescriptionScanResponse {
  items: DetectedDrugItem[]
}

export interface ConfirmedDrugItem {
  drug_id: number
  raw_text?: string | null
}

export interface PrescriptionConfirmResponse {
  results: DrugPricesResponse[]
}

export interface Pharmacy {
  id: number
  name: string
  address: string
  lat: number
  lng: number
  phone: string | null
  created_at: string
}

export interface PharmacyPriceOut {
  drug_id: number
  trade_name: string
  price: number
  in_stock: boolean
  updated_at: string
}

export interface CsvRowError {
  row_number: number
  raw: Record<string, unknown>
  error: string
}

export interface CsvUploadResult {
  imported: number
  errors: CsvRowError[]
}

export interface PharmacyInviteResponse {
  token: string
  pharmacy_id: number
  expires_at: string
}
