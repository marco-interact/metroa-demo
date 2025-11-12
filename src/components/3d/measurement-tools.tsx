"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Ruler, Download, Trash2, Check, X } from "lucide-react"

interface Measurement {
  id: number
  point1_id: number
  point2_id: number
  distance_meters: number
  distance_cm: number
  distance_mm: number
  label: string
  scaled: boolean
}

interface MeasurementToolsProps {
  scanId: string
  selectedPoints?: number[]
  onPointSelect?: (pointId: number) => void
  onSelectionModeChange?: (enabled: boolean) => void
  onClearPoints?: () => void
  className?: string
}

export function MeasurementTools({ 
  scanId, 
  selectedPoints: externalSelectedPoints = [],
  onPointSelect, 
  onSelectionModeChange,
  onClearPoints,
  className = "" 
}: MeasurementToolsProps) {
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [isCalibrating, setIsCalibrating] = useState(false)
  const [knownDistance, setKnownDistance] = useState("")
  const [measurementLabel, setMeasurementLabel] = useState("")
  const [isScaled, setIsScaled] = useState(false)
  
  // Use external selected points from parent
  const selectedPoints = externalSelectedPoints
  
  // Prevent infinite loops with ref
  const lastSelectionModeRef = useRef<boolean | undefined>(undefined)
  
  // Notify parent when selection mode changes - SAFE VERSION
  useEffect(() => {
    const needsSelection = isCalibrating || (isScaled && selectedPoints.length < 2)
    
    // Only call if value actually changed
    if (lastSelectionModeRef.current !== needsSelection && onSelectionModeChange) {
      lastSelectionModeRef.current = needsSelection
      // Use setTimeout to prevent blocking
      setTimeout(() => {
        try {
          onSelectionModeChange(needsSelection)
        } catch (error) {
          console.error('Error in onSelectionModeChange:', error)
        }
      }, 0)
    }
  }, [isCalibrating, isScaled, selectedPoints.length]) // Removed onSelectionModeChange from deps

  // Point selection is now handled by parent component
  // const handlePointClick = (pointId: number) => {
  //   if (selectedPoints.length < 2) {
  //     onPointSelect?.(pointId)
  //   }
  // }

  const handleCalibrateScale = async () => {
    if (selectedPoints.length !== 2 || !knownDistance) {
      alert("Select 2 points and enter known distance")
      return
    }

    try {
      const formData = new FormData()
      formData.append('scan_id', scanId)
      formData.append('point1_id', selectedPoints[0].toString())
      formData.append('point2_id', selectedPoints[1].toString())
      formData.append('known_distance', knownDistance)

      console.log('🔧 Calibrating with:', {
        scan_id: scanId,
        point1_id: selectedPoints[0],
        point2_id: selectedPoints[1],
        known_distance: knownDistance
      })

      const response = await fetch('/api/backend/measurements/calibrate', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        console.log('✅ Calibration success:', result)
        setIsScaled(true)
        setIsCalibrating(false)
        onClearPoints?.()  // Clear points via parent callback
        setKnownDistance("")
        alert(`Scale calibrated! Factor: ${result.scale_factor.toFixed(6)}`)
      } else {
        const errorText = await response.text()
        console.error('❌ Calibration failed:', response.status, errorText)
        alert(`Calibration failed: ${response.status} - ${errorText || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('❌ Calibration error:', error)
      alert(`Calibration failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const handleAddMeasurement = async () => {
    if (selectedPoints.length !== 2) {
      alert("Select 2 points to measure")
      return
    }

    try {
      const formData = new FormData()
      formData.append('scan_id', scanId)
      formData.append('point1_id', selectedPoints[0].toString())
      formData.append('point2_id', selectedPoints[1].toString())
      formData.append('label', measurementLabel || `Measurement ${measurements.length + 1}`)

      const response = await fetch('/api/backend/measurements/add', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setMeasurements([...measurements, result.measurement])
        onClearPoints?.()  // Clear points via parent callback
        setMeasurementLabel("")
      } else {
        alert('Failed to add measurement')
      }
    } catch (error) {
      console.error('Measurement error:', error)
      alert('Failed to add measurement')
    }
  }

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const response = await fetch(`/api/backend/measurements/${scanId}/export?format=${format}`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `measurements-${scanId}.${format}`
        a.click()
      }
    } catch (error) {
      console.error('Export error:', error)
    }
  }

  const handleDeleteMeasurement = (id: number) => {
    setMeasurements(measurements.filter(m => m.id !== id))
  }

  return (
    <Card className={`bg-app-card border-app-primary ${className}`}>
      <CardHeader>
        <CardTitle className="text-white font-mono flex items-center">
          <Ruler className="w-5 h-5 mr-2" />
          3D Measurements
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Scale Calibration Section */}
        {!isScaled && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-yellow-400">
              ⚠️ Calibrate Scale First
            </h3>
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-3 space-y-2">
              <p className="text-xs text-yellow-200 font-medium">How to calibrate:</p>
              <ol className="text-xs text-gray-300 space-y-1 list-decimal list-inside">
                <li>Click "Start Calibration" below</li>
                <li>Click 2 points in the 3D model that you know the distance between</li>
                <li>Enter the known distance in meters</li>
                <li>Click "Calibrate"</li>
              </ol>
              <p className="text-xs text-gray-400 italic">
                Example: Click two corners of a door (typically 0.9m or 2.1m apart)
              </p>
            </div>
            
            {!isCalibrating ? (
              <Button
                onClick={() => setIsCalibrating(true)}
                variant="outline"
                size="sm"
                className="w-full"
              >
                Start Calibration
              </Button>
            ) : (
              <div className="space-y-2">
                <Input
                  type="number"
                  step="0.001"
                  placeholder="Known distance (meters)"
                  value={knownDistance}
                  onChange={(e) => setKnownDistance(e.target.value)}
                  className="bg-app-elevated border-app-secondary"
                />
                <div className="text-xs text-gray-400">
                  Selected points: {selectedPoints.length}/2
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleCalibrateScale}
                    disabled={selectedPoints.length !== 2 || !knownDistance}
                    size="sm"
                    className="flex-1"
                  >
                    <Check className="w-4 h-4 mr-1" />
                    Calibrate
                  </Button>
                  <Button
                    onClick={() => {
                      setIsCalibrating(false)
                      onClearPoints?.()
                      setKnownDistance("")
                    }}
                    variant="outline"
                    size="sm"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Measurement Section */}
        {isScaled && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-green-400">
              ✓ Scale Calibrated
            </h3>
            
            <div className="space-y-2">
              <Input
                placeholder="Measurement label (optional)"
                value={measurementLabel}
                onChange={(e) => setMeasurementLabel(e.target.value)}
                className="bg-app-elevated border-app-secondary"
              />
              <div className="text-xs text-gray-400">
                Selected points: {selectedPoints.length}/2
              </div>
              <Button
                onClick={handleAddMeasurement}
                disabled={selectedPoints.length !== 2}
                size="sm"
                className="w-full"
              >
                <Ruler className="w-4 h-4 mr-1" />
                Add Measurement
              </Button>
            </div>
          </div>
        )}

        {/* Measurements List */}
        {measurements.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Measurements</h3>
              <div className="flex gap-1">
                <Button
                  onClick={() => handleExport('json')}
                  variant="outline"
                  size="sm"
                >
                  JSON
                </Button>
                <Button
                  onClick={() => handleExport('csv')}
                  variant="outline"
                  size="sm"
                >
                  CSV
                </Button>
              </div>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {measurements.map((m) => (
                <div
                  key={m.id}
                  className="bg-app-elevated border border-app-secondary rounded p-2 text-xs"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white font-semibold">{m.label}</span>
                    <Button
                      onClick={() => handleDeleteMeasurement(m.id)}
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                    >
                      <Trash2 className="w-3 h-3 text-red-400" />
                    </Button>
                  </div>
                  <div className="space-y-1 text-gray-400">
                    <div>{m.distance_meters.toFixed(3)} m</div>
                    <div>{m.distance_cm.toFixed(2)} cm</div>
                    <div>{m.distance_mm.toFixed(1)} mm</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>Click on points in the 3D viewer to select</p>
          {!isScaled && <p>• First: Calibrate scale with known distance</p>}
          {isScaled && <p>• Then: Add measurements between any points</p>}
        </div>
      </CardContent>
    </Card>
  )
}

