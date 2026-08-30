import { request } from './api'
import type { PrescriptionConfirmResponse, PrescriptionScanResponse } from '../types/api'

export function scanPrescription(image: File) {
  const formData = new FormData()
  formData.append('image', image)
  return request<PrescriptionScanResponse>('/prescriptions/scan', {
    method: 'POST',
    body: formData,
    isFormData: true,
  })
}

export function confirmPrescription(drugIds: number[]) {
  return request<PrescriptionConfirmResponse>('/prescriptions/confirm', {
    method: 'POST',
    body: { items: drugIds.map((drug_id) => ({ drug_id })) },
  })
}
