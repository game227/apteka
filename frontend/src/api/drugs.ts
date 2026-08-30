import { request } from './api'
import type { DrugAlternative, DrugPricesResponse, DrugSearchResult } from '../types/api'

export function searchDrugs(query: string) {
  return request<DrugSearchResult[]>('/drugs/search', { query: { q: query } })
}

export function fetchDrugPrices(drugId: number, coords?: { lat: number; lng: number }, radiusKm = 15) {
  return request<DrugPricesResponse>(`/drugs/${drugId}/prices`, {
    query: { lat: coords?.lat, lng: coords?.lng, radius_km: radiusKm },
  })
}

export function fetchDrugAlternatives(drugId: number) {
  return request<DrugAlternative[]>(`/drugs/${drugId}/alternatives`)
}
