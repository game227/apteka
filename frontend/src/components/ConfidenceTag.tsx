import type { ConfidenceLevel } from '../types/api'

const CONFIG: Record<ConfidenceLevel, { label: string; className: string }> = {
  high: { label: 'Yuqori ishonch', className: 'bg-green-100 text-green-800' },
  medium: { label: "O'rta ishonch", className: 'bg-yellow-100 text-yellow-800' },
  low: { label: 'Past ishonch', className: 'bg-red-100 text-red-800' },
}

export function ConfidenceTag({ level }: { level: ConfidenceLevel }) {
  const config = CONFIG[level]
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
