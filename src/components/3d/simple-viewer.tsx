"use client"

import { useRef, useEffect, useState } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { OrbitControls, Html } from "@react-three/drei"
import * as THREE from "three"
import { PLYLoader } from "three-stdlib"

interface SimpleViewerProps {
  modelUrl?: string
  className?: string
  onPointClick?: (pointIndex: number, position: [number, number, number]) => void
  enablePointSelection?: boolean
  selectedPointPositions?: Array<[number, number, number]>
}

// PLY Model Loader Component with Point Selection
function PLYModel({ url, onPointClick, enableSelection }: { 
  url: string
  onPointClick?: (pointIndex: number, position: [number, number, number]) => void
  enableSelection?: boolean
}) {
  const pointsRef = useRef<THREE.Points>(null)
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { camera, gl } = useThree()
  
  // Handle point cloud clicks for measurement
  const handleClick = (event: any) => {
    if (!enableSelection || !geometry || !onPointClick || !pointsRef.current) return
    
    try {
      event.stopPropagation()
      event.preventDefault()
      
      // Calculate mouse position in normalized device coordinates
      const canvas = gl.domElement
      const rect = canvas.getBoundingClientRect()
      const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const y = -((event.clientY - rect.top) / rect.height) * 2 + 1
      
      // Create raycaster with threshold for point clouds
      // Reference: https://threejs.org/docs/#api/en/core/Raycaster
      const raycaster = new THREE.Raycaster()
      raycaster.params.Points = { threshold: 0.15 } // Increase picking tolerance for points
      raycaster.setFromCamera(new THREE.Vector2(x, y), camera)
      
      // Find intersected points
      const intersects = raycaster.intersectObject(pointsRef.current, false)
      
      if (intersects.length > 0) {
        const intersection = intersects[0]
        const pointIndex = intersection.index ?? 0
        const position = intersection.point.toArray().slice(0, 3) as [number, number, number]
        
        console.log('✅ Point clicked:', { pointIndex, position })
        onPointClick(pointIndex, position)
      } else {
        console.log('⚠️ No point intersected - try clicking closer to a point')
      }
    } catch (error) {
      console.error('❌ Error in handleClick:', error)
    }
  }

  useEffect(() => {
    if (!url) return

    setLoading(true)
    setError(null)
    
    const loader = new PLYLoader()
    
    loader.load(
      url,
      (loadedGeometry) => {
        // Center the geometry
        loadedGeometry.computeBoundingBox()
        const center = new THREE.Vector3()
        loadedGeometry.boundingBox?.getCenter(center)
        loadedGeometry.translate(-center.x, -center.y, -center.z)
        
        // Normalize scale
        const box = new THREE.Box3().setFromBufferAttribute(
          loadedGeometry.attributes.position as THREE.BufferAttribute
        )
        const size = box.getSize(new THREE.Vector3())
        const maxDim = Math.max(size.x, size.y, size.z)
        const scale = 5 / maxDim
        loadedGeometry.scale(scale, scale, scale)
        
        setGeometry(loadedGeometry)
        setLoading(false)
        console.log('PLY loaded successfully:', url)
      },
      (progress) => {
        console.log('Loading progress:', (progress.loaded / progress.total * 100).toFixed(2) + '%')
      },
      (err) => {
        console.error('Error loading PLY:', err)
        setError('Failed to load 3D model')
        setLoading(false)
      }
    )
  }, [url])

  // Auto-rotation removed - only manual interaction now
  // useFrame(() => {
  //   if (pointsRef.current) {
  //     pointsRef.current.rotation.y += 0.001
  //   }
  // })

  if (loading) {
    return (
      <Html center>
        <div className="text-white text-sm bg-app-elevated/90 px-4 py-2 rounded">
          Loading 3D model...
        </div>
      </Html>
    )
  }

  if (error) {
    return (
      <Html center>
        <div className="text-red-400 text-sm bg-app-elevated/90 px-4 py-2 rounded">
          {error}
        </div>
      </Html>
    )
  }

  if (!geometry) return null

  return (
    <points 
      ref={pointsRef} 
      geometry={geometry}
      onClick={enableSelection ? handleClick : undefined}
      onPointerOver={enableSelection ? (e) => { e.stopPropagation(); document.body.style.cursor = 'crosshair' } : undefined}
      onPointerOut={enableSelection ? (e) => { e.stopPropagation(); document.body.style.cursor = 'default' } : undefined}
    >
      <pointsMaterial
        size={enableSelection ? 0.025 : 0.015}
        vertexColors
        sizeAttenuation
        transparent
        opacity={0.9}
      />
    </points>
  )
}

// Visual markers for selected points - Point A (Green) and Point B (Blue)
function PointMarkers({ positions }: { positions: Array<[number, number, number]> }) {
  return (
    <>
      {positions.map((pos, index) => {
        const pointLetter = index === 0 ? "A" : "B"
        const pointColor = index === 0 ? 0x10b981 : 0x3b82f6  // green-500 : blue-500
        const bgColor = index === 0 ? "bg-green-500" : "bg-blue-500"
        
        return (
          <group key={index} position={pos}>
            {/* Outer pulsing ring */}
            <mesh>
              <sphereGeometry args={[0.15, 16, 16]} />
              <meshBasicMaterial 
                color={pointColor} 
                transparent 
                opacity={0.4}
              />
            </mesh>
            
            {/* Inner solid sphere */}
            <mesh>
              <sphereGeometry args={[0.1, 16, 16]} />
              <meshBasicMaterial 
                color={pointColor}
                emissive={pointColor}
                emissiveIntensity={0.5}
              />
            </mesh>
            
            {/* Label with Point A/B */}
            <Html distanceFactor={10} center>
              <div className={`${bgColor} text-white px-3 py-1.5 rounded-lg text-sm font-bold shadow-lg pointer-events-none`}>
                Point {pointLetter}
                <div className="text-[10px] text-white/80 font-normal mt-0.5">
                  [{pos[0].toFixed(2)}, {pos[1].toFixed(2)}, {pos[2].toFixed(2)}]
                </div>
              </div>
            </Html>
          </group>
        )
      })}
    </>
  )
}

// Fallback point cloud component for demo
function DemoPointCloud({ visible = true }: { visible?: boolean }) {
  const pointsRef = useRef<THREE.Points>(null)
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)

  useEffect(() => {
    // Create a simple point cloud geometry
    const points = new Float32Array(30000)
    const colors = new Float32Array(30000)
    
    for (let i = 0; i < 10000; i++) {
      const radius = Math.random() * 5
      const theta = Math.random() * Math.PI * 2
      const phi = Math.random() * Math.PI
      
      points[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      points[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      points[i * 3 + 2] = radius * Math.cos(phi)
      
      colors[i * 3] = Math.random()
      colors[i * 3 + 1] = Math.random()
      colors[i * 3 + 2] = Math.random()
    }
    
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(points, 3))
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    setGeometry(geo)
  }, [])

  if (!geometry || !visible) return null

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.02}
        vertexColors
        sizeAttenuation
        transparent
        opacity={0.8}
      />
    </points>
  )
}

// Simple mesh component
function SimpleMesh({ visible = true }: { visible?: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)

  useEffect(() => {
    // Create a simple mesh geometry
    const geo = new THREE.BoxGeometry(2, 2, 2)
    setGeometry(geo)
  }, [])

  if (!geometry || !visible) return null

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial
        color="#4a90e2"
        wireframe={false}
        metalness={0.3}
        roughness={0.4}
      />
    </mesh>
  )
}

// Camera controller
function CameraController() {
  const { camera } = useThree()
  
  useEffect(() => {
    camera.position.set(5, 5, 5)
    camera.lookAt(0, 0, 0)
  }, [camera])

  return null
}

export function SimpleViewer({ 
  modelUrl, 
  className = "", 
  onPointClick, 
  enablePointSelection = false,
  selectedPointPositions = []
}: SimpleViewerProps) {
  const [viewMode, setViewMode] = useState<'pointcloud' | 'mesh'>('pointcloud')

  return (
    <div className={`relative bg-app-card rounded-lg overflow-hidden ${className}`}>
      {enablePointSelection && (
        <div className="absolute top-2 left-2 z-10 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary rounded-lg px-4 py-2 shadow-lg">
          <div className="text-white text-sm font-medium mb-1">🎯 Measurement Mode</div>
          <div className="flex items-center gap-3 text-xs">
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded ${selectedPointPositions.length >= 1 ? 'bg-green-500/30 border border-green-500' : 'bg-gray-700 border border-gray-600'}`}>
              <div className={`w-2 h-2 rounded-full ${selectedPointPositions.length >= 1 ? 'bg-green-500' : 'bg-gray-500'}`}></div>
              <span className={selectedPointPositions.length >= 1 ? 'text-green-100' : 'text-gray-400'}>Point A</span>
            </div>
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded ${selectedPointPositions.length >= 2 ? 'bg-blue-500/30 border border-blue-500' : 'bg-gray-700 border border-gray-600'}`}>
              <div className={`w-2 h-2 rounded-full ${selectedPointPositions.length >= 2 ? 'bg-blue-500' : 'bg-gray-500'}`}></div>
              <span className={selectedPointPositions.length >= 2 ? 'text-blue-100' : 'text-gray-400'}>Point B</span>
            </div>
            <div className="text-gray-400">
              {selectedPointPositions.length === 0 && "Click on model to place Point A"}
              {selectedPointPositions.length === 1 && "Click on model to place Point B"}
              {selectedPointPositions.length === 2 && "✅ Ready to calibrate"}
            </div>
          </div>
        </div>
      )}
      
      <Canvas
        camera={{ position: [5, 5, 5], fov: 75 }}
        className="bg-app-card"
        gl={{ antialias: false, powerPreference: "low-power" }}
        dpr={[1, 1.5]}
      >
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <directionalLight position={[-10, -10, -10]} intensity={0.3} />
        
        {/* Grid helper */}
        <gridHelper args={[20, 20, '#444444', '#222222']} />
        
        {/* Model content - Load actual PLY if URL provided, otherwise show demo */}
        {modelUrl ? (
          <PLYModel 
            url={modelUrl} 
            onPointClick={onPointClick}
            enableSelection={enablePointSelection}
          />
        ) : (
          <>
            {viewMode === 'pointcloud' ? (
              <DemoPointCloud visible={true} />
            ) : (
              <SimpleMesh visible={true} />
            )}
          </>
        )}
        
        {/* Visual markers for selected points */}
        {selectedPointPositions.length > 0 && (
          <PointMarkers positions={selectedPointPositions} />
        )}
        
        {/* Camera controls - Disabled during point selection */}
        <OrbitControls
          makeDefault
          enableDamping={true}
          dampingFactor={0.05}
          enablePan={true}
          enableZoom={true}
          enableRotate={!enablePointSelection}
          screenSpacePanning={true}
          minDistance={0.5}
          maxDistance={100}
          maxPolarAngle={Math.PI}
          rotateSpeed={0.6}
          panSpeed={1.0}
          zoomSpeed={1.2}
          enabled={!enablePointSelection}
        />
        
        <CameraController />
      </Canvas>

      {/* Controls - only show if no model URL (demo mode) */}
      {!modelUrl && (
        <div className="absolute top-4 right-4 z-10">
          <div className="bg-app-elevated/90 backdrop-blur-sm rounded-lg p-2">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('pointcloud')}
                className={`px-3 py-1 text-xs rounded ${
                  viewMode === 'pointcloud' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Points
              </button>
              <button
                onClick={() => setViewMode('mesh')}
                className={`px-3 py-1 text-xs rounded ${
                  viewMode === 'mesh' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Mesh
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Status indicator */}
      <div className="absolute bottom-4 left-4">
        <div className="bg-app-elevated/90 backdrop-blur-sm px-3 py-1 rounded-lg">
          <span className="text-white text-sm">
            {modelUrl ? '3D Point Cloud' : `Demo ${viewMode}`}
          </span>
        </div>
      </div>
    </div>
  )
}


