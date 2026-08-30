import { useEffect, useState } from 'react'
import { useDebounce } from '../hooks/useDebounce'

interface DrugSearchInputProps {
  onSearch: (query: string) => void
  placeholder?: string
  autoFocus?: boolean
}

export function DrugSearchInput({ onSearch, placeholder, autoFocus }: DrugSearchInputProps) {
  const [value, setValue] = useState('')
  const debounced = useDebounce(value, 350)

  useEffect(() => {
    onSearch(debounced.trim())
  }, [debounced, onSearch])

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder={placeholder ?? "Dori nomini kiriting..."}
      autoFocus={autoFocus}
      className="w-full rounded-xl border border-gray-300 px-4 py-3 text-base shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200"
    />
  )
}
