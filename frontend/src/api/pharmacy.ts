import { request } from './api'
import type { CsvUploadResult, Pharmacy, PharmacyMyPriceRow } from '../types/api'

export function fetchMyPharmacy() {
  return request<Pharmacy>('/pharmacy/my')
}

export function fetchMyPharmacyPrices() {
  return request<PharmacyMyPriceRow[]>('/pharmacy/my/prices')
}

export function upsertMyPrice(input: { drug_id: number; price: number; in_stock: boolean }) {
  return request<PharmacyMyPriceRow>('/pharmacy/my/prices', { method: 'POST', body: input })
}

export function uploadPricesCsv(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request<CsvUploadResult>('/pharmacy/my/prices/csv', {
    method: 'POST',
    body: formData,
    isFormData: true,
  })
}
