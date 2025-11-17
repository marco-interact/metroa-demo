"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { OrbitControls, Environment, Html, useGLTF } from "@react-three/drei"
import { PLYLoader } from "three-stdlib"
import { 
  Maximize2, 
  Minimize2, 
  RotateCcw, 
  Download,
  Eye,
  EyeOff,
  Ruler,
  Square
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import * as THREE from "three"

interface ModelViewerProps {
  modelUrl?: string
  pointCloudUrl?: string
  className?: string
  showControls?: boolean
  autoRotate?: boolean
}

interface MeasurementPoint {
  position: THREE.Vector3
  id: string
}

// PLY Point Cloud Loader Component with Performance Optimization
function PLYModel({ url }: { url: string }) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!url) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    // Use requestIdleCallback to load in background without blocking UI
    const loadInBackground = () => {
      try {
        const loader = new PLYLoader()
        loader.load(
          url,
          (geometry) => {
            if (geometry) {
              // Optimize geometry for rendering
              geometry.computeVertexNormals()
              
              // Downsample if too many points (prevents UI freeze)
              const vertexCount = geometry.attributes.position?.count || 0
              if (vertexCount > 500000) {
                console.log(`⚠️  Large point cloud (${vertexCount.toLocaleString()} points), downsampling for performance...`)
                // Downsample to max 500K points
                const step = Math.ceil(vertexCount / 500000)
                const positions = geometry.attributes.position.array
                const colors = geometry.attributes.color?.array
                
                const newPositions = []
                const newColors = []
                
                for (let i = 0; i < vertexCount; i += step) {
                  newPositions.push(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2])
                  if (colors) {
                    newColors.push(colors[i * 3], colors[i * 3 + 1], colors[i * 3 + 2])
                  }
                }
                
                const newGeometry = new THREE.BufferGeometry()
                newGeometry.setAttribute('position', new THREE.Float32BufferAttribute(newPositions, 3))
                if (newColors.length > 0) {
                  newGeometry.setAttribute('color', new THREE.Float32BufferAttribute(newColors, 3))
                }
                newGeometry.computeVertexNormals()
                
                setGeometry(newGeometry)
                console.log(`✅ Point cloud loaded and downsampled: ${newPositions.length / 3} points (from ${vertexCount})`)
              } else {
                setGeometry(geometry)
                console.log('✅ PLY file loaded successfully:', {
                  vertices: vertexCount,
                  hasColors: !!geometry.attributes.color
                })
              }
            }
            setLoading(false)
          },
          (progress) => {
            if (progress.total > 0) {
              const percent = (progress.loaded / progress.total) * 100
              if (percent % 10 < 1) { // Log every 10%
                console.log(`Loading PLY: ${percent.toFixed(0)}%`)
              }
            }
          },
          (error) => {
            console.error('❌ Error loading PLY file:', error)
            setError('Failed to load 3D model')
            setLoading(false)
          }
        )
      } catch (err) {
        console.error('❌ Error initializing PLY loader:', err)
        setError('Failed to initialize 3D model loader')
        setLoading(false)
      }
    }
    
    // Load in background to prevent UI blocking
    if ('requestIdleCallback' in window) {
      requestIdleCallback(loadInBackground, { timeout: 2000 })
    } else {
      setTimeout(loadInBackground, 0)
    }
  }, [url])

  if (loading) {
    return (
      <Html center>
        <div className="text-white text-sm">Loading 3D model...</div>
      </Html>
    )
  }

  if (error || !geometry) {
    return (
      <Html center>
        <div className="text-red-400 text-sm">{error || 'Model not available'}</div>
      </Html>
    )
  }

  return (
    <points>
      <bufferGeometry attach="geometry" {...geometry} />
      <pointsMaterial
        size={0.002}
        vertexColors
        sizeAttenuation
        transparent
        opacity={0.95}
      />
    </points>
  )
}

interface ViewerControlsProps {
  onReset: () => void
  onToggleWireframe: () => void
  onTogglePointCloud: () => void
  onToggleMeasurement: () => void
  onDownload: () => void
  wireframe: boolean
  showPointCloud: boolean
  measurementMode: boolean
  isFullscreen: boolean
  onToggleFullscreen: () => void
}

function ViewerControls({
  onReset,
  onToggleWireframe,
  onTogglePointCloud,
  onToggleMeasurement,
  onDownload,
  wireframe,
  showPointCloud,
  measurementMode,
  isFullscreen,
  onToggleFullscreen
}: ViewerControlsProps) {
  return (
    <div className="absolute top-4 right-4 z-10">
      <Card className="p-2 bg-app-card/90 backdrop-blur-sm border-app-secondary">
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleFullscreen}
            title={isFullscreen ? "Salir de pantalla completa" : "Pantalla completa"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            title="Restablecer vista"
          >
            <RotateCcw className="w-4 h-4" />
          </Button>
          
          <Button
            variant={wireframe ? "default" : "ghost"}
            size="sm"
            onClick={onToggleWireframe}
            title="Toggle wireframe"
          >
            <Square className="w-4 h-4" />
          </Button>
          
          <Button
            variant={showPointCloud ? "default" : "ghost"}
            size="sm"
            onClick={onTogglePointCloud}
            title="Toggle point cloud"
          >
            {showPointCloud ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </Button>
          
          <Button
            variant={measurementMode ? "default" : "ghost"}
            size="sm"
            onClick={onToggleMeasurement}
            title="Herramienta de medición"
          >
            <Ruler className="w-4 h-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onDownload}
            title="Descargar modelo"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    </div>
  )
}

function Model({ url, wireframe }: { url: string; wireframe: boolean }) {
  const { scene } = useGLTF(url)
  const meshRef = useRef<THREE.Group>(null)

  useEffect(() => {
    if (meshRef.current) {
      meshRef.current.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh
          if (mesh.material) {
            if (Array.isArray(mesh.material)) {
              mesh.material.forEach(mat => {
                if (mat instanceof THREE.MeshStandardMaterial) {
                  mat.wireframe = wireframe
                }
              })
            } else if (mesh.material instanceof THREE.MeshStandardMaterial) {
              mesh.material.wireframe = wireframe
            }
          }
        }
      })
    }
  }, [wireframe])

  return <primitive ref={meshRef} object={scene} />
}

function PointCloud({ points, visible }: { points: Float32Array; visible: boolean }) {
  const pointsRef = useRef<THREE.Points>(null)
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(points, 3))
  
  const material = new THREE.PointsMaterial({
    color: 0x88ccee,
    size: 0.005,
    sizeAttenuation: true
  })

  return visible ? (
    <points ref={pointsRef} geometry={geometry} material={material} />
  ) : null
}

function CameraController({ onReset, measurementMode }: { onReset: boolean; measurementMode?: boolean }) {
  const { camera, gl } = useThree()
  const controlsRef = useRef<any>()

  useEffect(() => {
    if (onReset && controlsRef.current) {
      controlsRef.current.reset()
    }
  }, [onReset])

  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.enabled = !measurementMode
    }
  }, [measurementMode])

  return (
    <OrbitControls
      ref={controlsRef}
      args={[camera, gl.domElement]}
      enableDamping={true}
      dampingFactor={0.05}
      screenSpacePanning={false}
      minDistance={1}
      maxDistance={100}
      maxPolarAngle={Math.PI}
      enabled={!measurementMode}
    />
  )
}

function MeasurementTool({ 
  enabled, 
  points, 
  onAddPoint 
}: { 
  enabled: boolean
  points: MeasurementPoint[]
  onAddPoint: (point: THREE.Vector3) => void 
}) {
  const { camera, raycaster, scene, gl } = useThree()
  
  const handleClick = useCallback((event: MouseEvent) => {
    if (!enabled) return
    
    try {
      event.preventDefault()
      event.stopPropagation()
      
      const canvas = gl.domElement
      const rect = canvas.getBoundingClientRect()
      
      // Normalized device coordinates (-1 to +1)
      const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const y = -((event.clientY - rect.top) / rect.height) * 2 + 1
      
      // Update raycaster
      raycaster.setFromCamera(new THREE.Vector2(x, y), camera)
      
      // Collect all intersectable objects (meshes AND point clouds)
      const intersectableObjects: THREE.Object3D[] = []
      scene.traverse((object) => {
        if (object.visible) {
          if ((object as THREE.Mesh).isMesh || (object as THREE.Points).isPoints) {
            intersectableObjects.push(object)
          }
        }
      })
      
      if (intersectableObjects.length === 0) {
        console.warn('No intersectable objects found in scene')
        return
      }
      
      // Raycast against all objects
      const intersects = raycaster.intersectObjects(intersectableObjects, false)
      
      if (intersects.length > 0) {
        const hitPoint = intersects[0].point.clone()
        console.log('✅ Point clicked:', hitPoint)
        onAddPoint(hitPoint)
      } else {
        console.log('⚠️ No intersection found at click position')
      }
    } catch (error) {
      console.error('❌ Error in handleClick:', error)
    }
  }, [enabled, camera, raycaster, scene, gl, onAddPoint])

  useEffect(() => {
    if (!enabled) return
    
    const canvas = gl.domElement
    if (!canvas) return
    
    canvas.style.cursor = 'crosshair'
    canvas.addEventListener('click', handleClick, true) // Use capture phase
    
    return () => {
      canvas.style.cursor = 'default'
      canvas.removeEventListener('click', handleClick, true)
    }
  }, [enabled, handleClick, gl])

  return (
    <>
      {points.map((point, index) => {
        // Color code points: GREEN for Point A, BLUE for Point B
        const pointLetter = index === 0 ? "A" : "B"
        const pointColor = index === 0 ? 0x10b981 : 0x3b82f6  // green-500 : blue-500
        const bgColor = index === 0 ? "bg-green-500" : "bg-blue-500"
        
        return (
          <group key={point.id}>
            {/* Large visible sphere */}
            <mesh position={point.position}>
              <sphereGeometry args={[0.1, 32, 32]} />
              <meshBasicMaterial 
                color={pointColor} 
                transparent
                opacity={0.9}
              />
            </mesh>
            
            {/* Outer ring for visibility */}
            <mesh position={point.position} rotation={[Math.PI / 2, 0, 0]}>
              <ringGeometry args={[0.12, 0.15, 32]} />
              <meshBasicMaterial 
                color={pointColor} 
                transparent 
                opacity={0.5}
                side={THREE.DoubleSide}
              />
            </mesh>
            
            {/* Simple label */}
            <Html position={[point.position.x, point.position.y + 0.2, point.position.z]} center>
              <div className={`${bgColor} text-white px-3 py-1 rounded font-bold text-sm shadow-lg`}>
                Point {pointLetter}
              </div>
            </Html>
          </group>
        )
      })}
      
      {points.length === 2 && (
        <>
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([
                  points[0].position.x, points[0].position.y, points[0].position.z,
                  points[1].position.x, points[1].position.y, points[1].position.z
                ])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#ff4444" linewidth={2} />
          </line>
          
          <Html
            position={[
              (points[0].position.x + points[1].position.x) / 2,
              (points[0].position.y + points[1].position.y) / 2,
              (points[0].position.z + points[1].position.z) / 2
            ]}
            distanceFactor={10}
          >
            <div className="bg-primary-500 text-white px-2 py-1 rounded text-xs font-medium">
              {points[0].position.distanceTo(points[1].position).toFixed(2)}m
            </div>
          </Html>
        </>
      )}
    </>
  )
}

export function ModelViewer({ 
  modelUrl,
  pointCloudUrl,
  className = "",
  showControls = true,
  autoRotate = false 
}: ModelViewerProps) {
  const [wireframe, setWireframe] = useState(false)
  const [showPointCloud, setShowPointCloud] = useState(true)
  const [measurementMode, setMeasurementMode] = useState(false)
  const [measurementPoints, setMeasurementPoints] = useState<MeasurementPoint[]>([])
  const [resetCamera, setResetCamera] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Generate demo point cloud data for testing
  const demoPointCloud = new Float32Array(30000)
  for (let i = 0; i < 10000; i++) {
    demoPointCloud[i * 3] = (Math.random() - 0.5) * 10
    demoPointCloud[i * 3 + 1] = (Math.random() - 0.5) * 10
    demoPointCloud[i * 3 + 2] = (Math.random() - 0.5) * 10
  }

  const handleAddMeasurementPoint = useCallback((point: THREE.Vector3) => {
    console.log('handleAddMeasurementPoint called with point:', point)
    setMeasurementPoints(prev => {
      console.log('Current measurement points:', prev.length)
      if (prev.length >= 2) {
        // Reset and start new measurement
        return [{ position: point, id: Date.now().toString() }]
      } else {
        // Add point
        return [...prev, { position: point, id: Date.now().toString() }]
      }
    })
  }, [])

  const handleReset = () => {
    setResetCamera(true)
    setMeasurementPoints([])
    setTimeout(() => setResetCamera(false), 100)
  }

  const handleToggleMeasurement = () => {
    setMeasurementMode(!measurementMode)
    if (measurementMode) {
      setMeasurementPoints([])
    }
  }

  const handleDownload = () => {
    // Implement download functionality
    console.log('Download model')
  }

  const handleToggleFullscreen = () => {
    if (!isFullscreen) {
      containerRef.current?.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  // No artificial loading delay

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {loading && (
        <div className="absolute inset-0 bg-app-primary flex items-center justify-center z-20">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-400">Cargando modelo 3D...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 bg-app-primary flex items-center justify-center z-20">
          <div className="text-center">
            <h3 className="text-lg font-medium text-white mb-2">Error al cargar el modelo</h3>
            <p className="text-gray-400">{error}</p>
          </div>
        </div>
      )}

      <Canvas
        camera={{ position: [5, 5, 5], fov: 75 }}
        className="bg-app-primary"
        gl={{ antialias: false, powerPreference: "low-power" }}
        dpr={[1, 1.5]}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <directionalLight position={[-10, -10, -10]} intensity={0.5} />
        
        {/* Environment for better reflections */}
        <Environment preset="city" />
        
        {/* Load real PLY model if URL provided, otherwise show demo cube */}
        {pointCloudUrl ? (
          <PLYModel url={pointCloudUrl} />
        ) : modelUrl ? (
          <PLYModel url={modelUrl} />
        ) : (
          <>
            {/* Demo cube since we don't have actual models */}
            <mesh>
              <boxGeometry args={[2, 2, 2]} />
              <meshStandardMaterial 
                color="#4a90e2" 
                wireframe={wireframe}
                metalness={0.3}
                roughness={0.4}
              />
            </mesh>
            
            {/* Point cloud */}
            {showPointCloud && <PointCloud points={demoPointCloud} visible={true} />}
          </>
        )}
        
        {/* Measurement tool */}
        <MeasurementTool 
          enabled={measurementMode}
          points={measurementPoints}
          onAddPoint={handleAddMeasurementPoint}
        />
        
        {/* Camera controls */}
        <CameraController onReset={resetCamera} measurementMode={measurementMode} />
        
        {/* Grid */}
        <gridHelper args={[20, 20, '#333333', '#333333']} />
      </Canvas>

      {/* Controls */}
      {showControls && (
        <ViewerControls
          onReset={handleReset}
          onToggleWireframe={() => setWireframe(!wireframe)}
          onTogglePointCloud={() => setShowPointCloud(!showPointCloud)}
          onToggleMeasurement={handleToggleMeasurement}
          onDownload={handleDownload}
          wireframe={wireframe}
          showPointCloud={showPointCloud}
          measurementMode={measurementMode}
          isFullscreen={isFullscreen}
          onToggleFullscreen={handleToggleFullscreen}
        />
      )}

      {/* Measurement info with colored indicators */}
      {measurementMode && (
        <div className="absolute bottom-4 left-4 z-10">
          <Card className="p-4 bg-app-card/90 backdrop-blur-sm border-app-secondary">
            <div className="text-sm text-white space-y-2">
              <p className="font-medium mb-2">🎯 Herramienta de Medición</p>
              
              {/* Point selection status with A/B nomenclature */}
              <div className="flex items-center gap-2 text-xs">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${measurementPoints.length >= 1 ? 'bg-green-500/30 border-2 border-green-500 shadow-lg shadow-green-500/20' : 'bg-gray-700 border-2 border-gray-600'}`}>
                  <div className={`w-3 h-3 rounded-full ${measurementPoints.length >= 1 ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                  <span className={measurementPoints.length >= 1 ? 'text-green-100' : 'text-gray-400'}>Point A</span>
                  {measurementPoints.length >= 1 && <span className="text-green-300">✓</span>}
                </div>
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${measurementPoints.length >= 2 ? 'bg-blue-500/30 border-2 border-blue-500 shadow-lg shadow-blue-500/20' : 'bg-gray-700 border-2 border-gray-600'}`}>
                  <div className={`w-3 h-3 rounded-full ${measurementPoints.length >= 2 ? 'bg-blue-500 animate-pulse' : 'bg-gray-500'}`}></div>
                  <span className={measurementPoints.length >= 2 ? 'text-blue-100' : 'text-gray-400'}>Point B</span>
                  {measurementPoints.length >= 2 && <span className="text-blue-300">✓</span>}
                </div>
              </div>
              
              <p className="text-gray-300 text-sm font-medium">
                {measurementPoints.length === 0 && "Click on model to place Point A (🟢 Green)"}
                {measurementPoints.length === 1 && "Click on model to place Point B (🔵 Blue)"}
                {measurementPoints.length === 2 && "✅ Measurement Complete! Click to restart."}
              </p>
              
              {measurementPoints.length === 2 && (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="mt-2 w-full"
                  onClick={() => setMeasurementPoints([])}
                >
                  🔄 New Measurement
                </Button>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}