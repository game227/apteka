import { useEffect, useState } from 'react'

export const TASHKENT_CENTER = { lat: 41.3111, lng: 69.2797 }

interface GeolocationState {
  coords: { lat: number; lng: number }
  isPrecise: boolean
  isLoading: boolean
}

export function useGeolocation(): GeolocationState {
  const [state, setState] = useState<GeolocationState>({
    coords: TASHKENT_CENTER,
    isPrecise: false,
    isLoading: true,
  })

  useEffect(() => {
    if (!navigator.geolocation) {
      setState((s) => ({ ...s, isLoading: false }))
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          coords: { lat: position.coords.latitude, lng: position.coords.longitude },
          isPrecise: true,
          isLoading: false,
        })
      },
      () => {
        setState((s) => ({ ...s, isLoading: false }))
      },
      { timeout: 8000 },
    )
  }, [])

  return state
}
