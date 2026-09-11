'use client'

/**
 * LocationPicker Component
 * 
 * Allows users to input GPS coordinates manually or use browser geolocation
 */

import { useState } from 'react'
import { MapPin, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FormError } from '@/components/ui/form-error'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface LocationPickerProps {
  latitude: number | null
  longitude: number | null
  onLocationChange: (lat: number | null, lng: number | null) => void
  latitudeError?: string
  longitudeError?: string
  disabled?: boolean
}

export function LocationPicker({
  latitude,
  longitude,
  onLocationChange,
  latitudeError,
  longitudeError,
  disabled = false,
}: LocationPickerProps) {
  const [isGettingLocation, setIsGettingLocation] = useState(false)
  const [locationError, setLocationError] = useState<string | null>(null)

  /**
   * Get current location using browser geolocation API
   */
  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser')
      return
    }

    setIsGettingLocation(true)
    setLocationError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsGettingLocation(false)
        onLocationChange(
          position.coords.latitude,
          position.coords.longitude
        )
      },
      (error) => {
        setIsGettingLocation(false)
        
        let errorMessage = 'Failed to get location'
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please enable location access in your browser settings.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable'
            break
          case error.TIMEOUT:
            errorMessage = 'Location request timed out'
            break
        }
        
        setLocationError(errorMessage)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  }

  /**
   * Clear location
   */
  const handleClearLocation = () => {
    onLocationChange(null, null)
    setLocationError(null)
  }

  const hasLocation = latitude !== null && longitude !== null

  return (
    <div className="space-y-4">
      {/* Get location button */}
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={handleGetCurrentLocation}
          disabled={disabled || isGettingLocation}
          className="gap-2"
        >
          {isGettingLocation ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Getting Location...
            </>
          ) : (
            <>
              <MapPin className="h-4 w-4" />
              Use Current Location
            </>
          )}
        </Button>

        {hasLocation && (
          <Button
            type="button"
            variant="ghost"
            onClick={handleClearLocation}
            disabled={disabled}
            size="sm"
          >
            Clear
          </Button>
        )}
      </div>

      {/* Info */}
      <p className="text-sm text-gray-500">
        GPS coordinates are optional but help precisely locate the challenge.
      </p>

      {/* Location error */}
      {locationError && (
        <Alert variant="destructive">
          <AlertDescription>{locationError}</AlertDescription>
        </Alert>
      )}

      {/* Manual coordinate inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Latitude */}
        <div className="space-y-2">
          <Label htmlFor="latitude">
            Latitude
          </Label>
          <Input
            id="latitude"
            name="latitude"
            type="number"
            step="any"
            min={-90}
            max={90}
            placeholder="e.g., 23.3441"
            value={latitude !== null ? latitude : ''}
            onChange={(e) => {
              const value = e.target.value
              onLocationChange(
                value ? parseFloat(value) : null,
                longitude
              )
              setLocationError(null)
            }}
            disabled={disabled}
            aria-invalid={!!latitudeError}
            aria-describedby={latitudeError ? 'latitude-error' : undefined}
          />
          {latitudeError && (
            <FormError id="latitude-error" message={latitudeError} />
          )}
          <p className="text-xs text-gray-500">Range: -90 to 90</p>
        </div>

        {/* Longitude */}
        <div className="space-y-2">
          <Label htmlFor="longitude">
            Longitude
          </Label>
          <Input
            id="longitude"
            name="longitude"
            type="number"
            step="any"
            min={-180}
            max={180}
            placeholder="e.g., 85.3096"
            value={longitude !== null ? longitude : ''}
            onChange={(e) => {
              const value = e.target.value
              onLocationChange(
                latitude,
                value ? parseFloat(value) : null
              )
              setLocationError(null)
            }}
            disabled={disabled}
            aria-invalid={!!longitudeError}
            aria-describedby={longitudeError ? 'longitude-error' : undefined}
          />
          {longitudeError && (
            <FormError id="longitude-error" message={longitudeError} />
          )}
          <p className="text-xs text-gray-500">Range: -180 to 180</p>
        </div>
      </div>

      {/* Current location display */}
      {hasLocation && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">
            <MapPin className="inline h-4 w-4 mr-1" />
            Location set: {latitude?.toFixed(6)}, {longitude?.toFixed(6)}
          </p>
        </div>
      )}
    </div>
  )
}
