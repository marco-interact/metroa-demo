"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Ruler, Download, Trash2, Check, X, Triangle, Layers, Circle, Info } from "lucide-react"

export type MeasurementType = "distance" | "angle" | "thickness" | "radius" | "info"

interface BaseMeasurement {
  id: number
  type: MeasurementType
  label: string
  scaled: boolean
}

interface DistanceMeasurement extends BaseMeasurement {
  type: "distance"
  point1_id: number
  point2_id: number
  distance_meters: number
  distance_cm: number
  distance_mm: number
}

interface AngleMeasurement extends BaseMeasurement {
  type: "angle"
  point1_id: number
  point2_id: number  // Vertex
  point3_id: number
  angle_degrees: number
}

interface ThicknessMeasurement extends BaseMeasurement {
  type: "thickness"
  point1_id: number
  point2_id: number
  thickness_meters: number
}

interface RadiusMeasurement extends BaseMeasurement {
  type: "radius"
  points: number[]  // 3+ point IDs
  radius_meters: number
  center: [number, number, number]
}

interface InfoMeasurement extends BaseMeasurement {
  type: "info"
  point_id: number
  position: [number, number, number]
  normal?: [number, number, number]
}

type Measurement = DistanceMeasurement | AngleMeasurement | ThicknessMeasurement | RadiusMeasurement | InfoMeasurement

interface MeasurementToolsProps {
  scanId: string
  selectedPoints?: number[]
  selectedPointPositions?: Array<[number, number, number]>
  onPointSelect?: (pointId: number) => void
  onSelectionModeChange?: (enabled: boolean) => void
  onClearPoints?: () => void
  className?: string
}

const MEASUREMENT_TYPE_INFO: Record<MeasurementType, { 
  name: string
  icon: typeof Ruler
  pointsRequired: number
  description: string
}> = {
  distance: {
    name: "Distance",
    icon: Ruler,
    pointsRequired: 2,
    description: "Measure distance between two points"
  },
  angle:   {
    name: "Angle",
    icon: Triangle,
    pointsRequired: 3,
    description: "Measure angle between three points (vertex in middle)"
  },
  thickness: {
    name: "Thickness",
    icon: Layers,
    pointsRequired: 2,
    description: "Measure thickness between two surfaces"
  },
  radius: {
    name: "Radius",
    icon: Circle,
    pointsRequired: 3,
    description: "Measure radius of curvature (3+ points on curve)"
  },
  info: {
    name: "Point Info",
    icon: Info,
    pointsRequired: 1,
    description: "Get coordinates and normal of a point"
  }
}

export function MeasurementTools({ 
  scanId, 
  selectedPoints: externalSelectedPoints = [],
  selectedPointPositions: externalSelectedPositions = [],
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
  const [measurementType, setMeasurementType] = useState<MeasurementType>("distance")
  
  // Use external selected points from parent
  const selectedPoints = externalSelectedPoints
  const selectedPointPositions = externalSelectedPositions
  
  // Prevent infinite loops with ref
  const lastSelectionModeRef = useRef<boolean | undefined>(undefined)
  
  const currentTypeInfo = MEASUREMENT_TYPE_INFO[measurementType]
  const pointsRequired = currentTypeInfo.pointsRequired
  
  // Notify parent when selection mode changes - SAFE VERSION
  useEffect(() => {
    const needsSelection = isCalibrating || (isScaled && selectedPointPositions.length < pointsRequired)
    
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
  }, [isCalibrating, isScaled, selectedPointPositions.length, pointsRequired, onSelectionModeChange])

  const handleCalibrateScale = async () => {
    // Safety checks
    if (!externalSelectedPositions || externalSelectedPositions.length !== 2) {
      alert("❌ Please select exactly 2 points in the 3D model.\n\nMake sure you're in Orbit mode and click directly on the model.")
      return
    }
    
    if (!knownDistance || parseFloat(knownDistance) <= 0) {
      alert("❌ Please enter a valid known distance (must be greater than 0)")
      return
    }

    try {
      const formData = new FormData()
      formData.append('scan_id', scanId)
      formData.append('point1_position', JSON.stringify(externalSelectedPositions[0]))
      formData.append('point2_position', JSON.stringify(externalSelectedPositions[1]))
      formData.append('known_distance', knownDistance)

      console.log('🔧 Calibrating with positions:', {
        scan_id: scanId,
        point1_position: externalSelectedPositions[0],
        point2_position: externalSelectedPositions[1],
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
        onClearPoints?.()
        setKnownDistance("")
        alert(`Scale calibrated! Factor: ${result.scale_factor.toFixed(6)}`)
      } else {
        const errorText = await response.text()
        console.error('❌ Calibration failed:', response.status, errorText)
        let errorMessage = 'Unknown error'
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        alert(`Calibration failed: ${errorMessage}`)
      }
    } catch (error) {
      console.error('❌ Calibration error:', error)
      alert(`Calibration failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const handleAddMeasurement = async () => {
    // Safety checks
    if (!externalSelectedPositions || externalSelectedPositions.length < pointsRequired) {
      alert(`❌ Please select ${pointsRequired} point(s) to measure ${currentTypeInfo.name.toLowerCase()}.\n\nMake sure you're in Orbit mode and click directly on the model.\n\nCurrent points: ${externalSelectedPositions?.length || 0}/${pointsRequired}`)
      return
    }

    try {
      const formData = new FormData()
      formData.append('scan_id', scanId)
      formData.append('measurement_type', measurementType)
      formData.append('label', measurementLabel || `${currentTypeInfo.name} ${measurements.length + 1}`)
      
      // Add point positions based on measurement type
      if (measurementType === "distance" || measurementType === "thickness") {
        formData.append('point1_position', JSON.stringify(externalSelectedPositions[0]))
        formData.append('point2_position', JSON.stringify(externalSelectedPositions[1]))
      } else if (measurementType === "angle") {
        formData.append('point1_position', JSON.stringify(externalSelectedPositions[0]))
        formData.append('point2_position', JSON.stringify(externalSelectedPositions[1]))  // Vertex
        formData.append('point3_position', JSON.stringify(externalSelectedPositions[2]))
      } else if (measurementType === "radius") {
        // For radius, send all points
        formData.append('points', JSON.stringify(externalSelectedPositions))
      } else if (measurementType === "info") {
        formData.append('point_position', JSON.stringify(externalSelectedPositions[0]))
      }

      const response = await fetch('/api/backend/measurements/add', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setMeasurements([...measurements, result.measurement])
        onClearPoints?.()
        setMeasurementLabel("")
      } else {
        const errorText = await response.text()
        console.error('❌ Measurement failed:', errorText)
        alert(`Failed to add measurement: ${errorText}`)
      }
    } catch (error) {
      console.error('Measurement error:', error)
      alert(`Failed to add measurement: ${error instanceof Error ? error.message : 'Unknown error'}`)
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

  const renderMeasurementValue = (m: Measurement) => {
    switch (m.type) {
      case "distance":
        return (
          <div className="space-y-1 text-gray-400">
            <div>{m.distance_meters.toFixed(3)} m</div>
            <div>{m.distance_cm.toFixed(2)} cm</div>
            <div>{m.distance_mm.toFixed(1)} mm</div>
          </div>
        )
      case "angle":
        return (
          <div className="text-gray-400">
            <div className="text-lg font-semibold">{m.angle_degrees.toFixed(2)}°</div>
          </div>
        )
      case "thickness":
        return (
          <div className="space-y-1 text-gray-400">
            <div>{m.thickness_meters.toFixed(3)} m</div>
            <div>{(m.thickness_meters * 100).toFixed(2)} cm</div>
          </div>
        )
      case "radius":
        return (
          <div className="space-y-1 text-gray-400">
            <div>Radius: {m.radius_meters.toFixed(3)} m</div>
            <div className="text-xs">Points: {m.points.length}</div>
          </div>
        )
      case "info":
        return (
          <div className="space-y-1 text-gray-400 text-xs">
            <div>X: {m.position[0].toFixed(3)}</div>
            <div>Y: {m.position[1].toFixed(3)}</div>
            <div>Z: {m.position[2].toFixed(3)}</div>
            {m.normal && (
              <div className="mt-1 pt-1 border-t border-gray-600">
                <div>Normal: [{m.normal[0].toFixed(2)}, {m.normal[1].toFixed(2)}, {m.normal[2].toFixed(2)}]</div>
              </div>
            )}
          </div>
        )
    }
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
        {/* Important: Switch to Orbit Mode Notice */}
        <div className="bg-primary-400/10 border border-primary-400/30 rounded p-3 space-y-2">
          <p className="text-xs text-primary-400 font-semibold">📍 Measurement Tool Instructions:</p>
          <ol className="text-xs text-gray-300 space-y-1 list-decimal list-inside">
            <li><strong>Switch to "Orbit" mode</strong> using the toggle in the 3D viewer</li>
            <li>Click "Start Calibration" below</li>
            <li>Click points directly on the 3D model</li>
          </ol>
          <p className="text-xs text-yellow-400 italic">
            ⚠️ Point selection only works in Orbit mode, not First Person mode
          </p>
        </div>

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
                <div className={`text-xs font-mono ${selectedPointPositions.length === 2 ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="font-semibold">Selected points: {selectedPointPositions.length}/2</span>
                  {selectedPointPositions.length === 0 && (
                    <span className="block text-yellow-400 mt-1">
                      ⚠️ Switch to Orbit mode and click on the model
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleCalibrateScale}
                    disabled={selectedPointPositions.length !== 2 || !knownDistance}
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

        {/* Measurement Type Selector */}
        {isScaled && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-green-400">
              ✓ Scale Calibrated
            </h3>
            
            <div className="grid grid-cols-2 gap-2">
              {(Object.keys(MEASUREMENT_TYPE_INFO) as MeasurementType[]).map((type) => {
                const info = MEASUREMENT_TYPE_INFO[type]
                const Icon = info.icon
                const isSelected = measurementType === type
                
                return (
                  <Button
                    key={type}
                    onClick={() => {
                      setMeasurementType(type)
                      onClearPoints?.()
                    }}
                    variant={isSelected ? "default" : "outline"}
                    size="sm"
                    className={`flex flex-col items-center gap-1 h-auto py-2 ${
                      isSelected ? "bg-primary-500" : ""
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-xs">{info.name}</span>
                  </Button>
                )
              })}
            </div>
            
            <div className="bg-app-elevated border border-app-secondary rounded p-2 text-xs text-gray-400">
              {currentTypeInfo.description}
            </div>
          </div>
        )}

        {/* Measurement Input Section */}
        {isScaled && (
          <div className="space-y-2">
            <Input
              placeholder={`${currentTypeInfo.name} label (optional)`}
              value={measurementLabel}
              onChange={(e) => setMeasurementLabel(e.target.value)}
              className="bg-app-elevated border-app-secondary"
            />
            <div className={`text-xs font-mono ${selectedPointPositions.length >= pointsRequired ? 'text-green-400' : 'text-gray-400'}`}>
              <span className="font-semibold">Selected points: {selectedPointPositions.length}/{pointsRequired}</span>
              {selectedPointPositions.length === 0 && (
                <span className="block text-yellow-400 mt-1">
                  ⚠️ Switch to Orbit mode to select points
                </span>
              )}
              {selectedPointPositions.length > 0 && selectedPointPositions.length < pointsRequired && (
                <span className="block text-primary-400 mt-1">
                  ➡️ Select {pointsRequired - selectedPointPositions.length} more point(s)
                </span>
              )}
            </div>
            <Button
              onClick={handleAddMeasurement}
              disabled={selectedPointPositions.length < pointsRequired}
              size="sm"
              className="w-full"
            >
              <currentTypeInfo.icon className="w-4 h-4 mr-1" />
              Add {currentTypeInfo.name}
            </Button>
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
              {measurements.map((m) => {
                const typeInfo = MEASUREMENT_TYPE_INFO[m.type]
                const Icon = typeInfo.icon
                
                return (
                  <div
                    key={m.id}
                    className="bg-app-elevated border border-app-secondary rounded p-2 text-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <Icon className="w-3 h-3" />
                        <span className="text-white font-semibold">{m.label}</span>
                        <span className="text-gray-500 text-[10px]">({m.type})</span>
                      </div>
                      <Button
                        onClick={() => handleDeleteMeasurement(m.id)}
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                      >
                        <Trash2 className="w-3 h-3 text-red-400" />
                      </Button>
                    </div>
                    {renderMeasurementValue(m)}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>Click on points in the 3D viewer to select</p>
          {!isScaled && <p>• First: Calibrate scale with known distance</p>}
          {isScaled && (
            <>
              <p>• Select measurement type above</p>
              <p>• Click {pointsRequired} point(s) for {currentTypeInfo.name.toLowerCase()}</p>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
