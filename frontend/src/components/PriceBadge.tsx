interface PriceBadgeProps {
  price: number
  deviationPercent: number | null
  isOverpriced: boolean
}

function formatSom(value: number) {
  return `${value.toLocaleString('uz-UZ')} so'm`
}

export function PriceBadge({ price, deviationPercent, isOverpriced }: PriceBadgeProps) {
  const badgeClass = isOverpriced
    ? 'bg-red-50 text-red-700 border-red-200'
    : 'bg-green-50 text-green-700 border-green-200'

  return (
    <div className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 ${badgeClass}`}>
      <span className="font-semibold">{formatSom(price)}</span>
      {isOverpriced && deviationPercent !== null && (
        <span className="rounded bg-red-600 px-1.5 py-0.5 text-xs font-bold text-white">
          +{deviationPercent}% qimmat
        </span>
      )}
    </div>
  )
}
