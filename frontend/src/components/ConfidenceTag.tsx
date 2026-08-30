import type { PrescriptionItemStatus } from '../types/api'

const CONFIG: Record<PrescriptionItemStatus, { label: string; className: string }> = {
  matched: { label: 'Aniq topildi', className: 'bg-green-100 text-green-800' },
  needs_confirmation: { label: "Tasdiqlash kerak", className: 'bg-yellow-100 text-yellow-800' },
  not_found: { label: 'Topilmadi', className: 'bg-red-100 text-red-800' },
}

export function ConfidenceTag({ status }: { status: PrescriptionItemStatus }) {
  const config = CONFIG[status]
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
