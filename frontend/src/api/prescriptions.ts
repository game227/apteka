import { request } from './api'
import type { ConfirmedDrugItem, PrescriptionConfirmResponse, PrescriptionScanResponse } from '../types/api'

export function scanPrescription(image: File) {
  const formData = new FormData()
  formData.append('file', image)
  return request<PrescriptionScanResponse>('/prescriptions/scan', {
    method: 'POST',
    body: formData,
    isFormData: true,
  })
}

export function confirmPrescription(
  items: ConfirmedDrugItem[],
  coords?: { lat: number; lng: number },
  radiusKm = 15,
) {
  return request<PrescriptionConfirmResponse>('/prescriptions/confirm', {
    method: 'POST',
    body: { items, lat: coords?.lat ?? null, lng: coords?.lng ?? null, radius_km: radiusKm },
  })
}
