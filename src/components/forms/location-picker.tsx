"use client"

import { useEffect, useState } from "react"
import dynamic from "next/dynamic"
import { MapPin } from "lucide-react"

// Dynamically import Leaflet to avoid SSR issues
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
)
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
)
const useMapEvents = dynamic(
  () => import("react-leaflet").then((mod) => mod.useMapEvents),
  { ssr: false }
)

interface LocationPickerProps {
  value: string
  onChange: (location: string, lat: number, lng: number) => void
  className?: string
}

function LocationMarker({ 
  position, 
  setPosition 
}: { 
  position: [number, number] | null
  setPosition: (pos: [number, number]) => void 
}) {
  const map = useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
    },
  })

  return position === null ? null : <Marker position={position} />
}

export function LocationPicker({ value, onChange, className = "" }: LocationPickerProps) {
  const [position, setPosition] = useState<[number, number] | null>(null)
  const [address, setAddress] = useState(value)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Import Leaflet CSS
    import("leaflet/dist/leaflet.css")
  }, [])

  useEffect(() => {
    if (position) {
      // Reverse geocode to get address
      fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position[0]}&lon=${position[1]}`)
        .then(res => res.json())
        .then(data => {
          const addr = data.display_name || `${position[0].toFixed(6)}, ${position[1].toFixed(6)}`
          setAddress(addr)
          onChange(addr, position[0], position[1])
        })
        .catch(() => {
          const addr = `${position[0].toFixed(6)}, ${position[1].toFixed(6)}`
          setAddress(addr)
          onChange(addr, position[0], position[1])
        })
    }
  }, [position])

  const handlePositionChange = (pos: [number, number]) => {
    setPosition(pos)
  }

  if (!mounted) {
    return (
      <div className={`h-64 bg-app-elevated rounded-lg flex items-center justify-center ${className}`}>
        <MapPin className="w-8 h-8 text-gray-600" />
      </div>
    )
  }

  return (
    <div className={className}>
      <div className="mb-2">
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Click on map to select location
        </label>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Or type address..."
          className="w-full px-3 py-2 bg-app-elevated border border-app-secondary rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
      
      <div className="h-64 rounded-lg overflow-hidden border border-app-secondary">
        <MapContainer
          center={position || [25.6866, -100.3161]} // Default: Monterrey, Mexico
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LocationMarker position={position} setPosition={handlePositionChange} />
        </MapContainer>
      </div>
      
      {position && (
        <p className="mt-2 text-xs text-gray-400">
          Coordinates: {position[0].toFixed(6)}, {position[1].toFixed(6)}
        </p>
      )}
    </div>
  )
}

