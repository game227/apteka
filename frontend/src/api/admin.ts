import { request } from './api'
import type { Pharmacy, PharmacyInviteResponse } from '../types/api'

export function fetchPharmacies() {
  return request<Pharmacy[]>('/admin/pharmacies')
}

export function createPharmacy(input: { name: string; address: string; lat: number; lng: number; phone: string }) {
  return request<Pharmacy>('/admin/pharmacies', { method: 'POST', body: input })
}

export function createPharmacyInvite(pharmacyId: number) {
  return request<PharmacyInviteResponse>(`/admin/pharmacies/${pharmacyId}/invite`, { method: 'POST' })
}
