"use client"

import { useRef, useEffect, useState, useCallback, useMemo } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { PointerLockControls, Stats } from "@react-three/drei"
import * as THREE from "three"
import { PLYLoader } from "three-stdlib"
import { RotateCcw, Maximize2, Minimize2, Eye, EyeOff, Info, X, Gauge } from "lucide-react"
import { Octree } from "@/utils/octree"
import { getDeviceType, getOptimalPointCloudSize, getCanvasConfig, shouldEnableCollision, getPointSize } from "@/utils/mobile"

// ==================== TYPES ====================

interface FirstPersonViewerProps {
  plyUrl: string
  scanId: string
  initialSpeed?: number
  initialPosition?: [number, number, number]
  onPositionChange?: (position: THREE.Vector3) => void
  onRotationChange?: (rotation: { pitch: number; yaw: number }) => void
  className?: string
  showStats?: boolean
}

interface FirstPersonControllerProps {
  speed: number
  enabled: boolean
  octree: Octree | null
  collisionRadius?: number
  acceleration?: number
  deceleration?: number
  minPolarAngle?: number
  maxPolarAngle?: number
}

interface KeyboardState {
  forward: boolean
  backward: boolean
  left: boolean
  right: boolean
  up: boolean
  down: boolean
  sprint: boolean
}

interface VelocityState {
  forward: number
  right: number
  vertical: number
}

// ==================== FIRST PERSON CONTROLLER (WITH COLLISION) ====================

function FirstPersonController({ 
  speed, 
  enabled, 
  octree,
  collisionRadius = 0.3,
  acceleration = 8,
  deceleration = 10,
}: FirstPersonControllerProps) {
  const { camera } = useThree()
  
  const keysPressed = useRef<KeyboardState>({
    forward: false,
    backward: false,
    left: false,
    right: false,
    up: false,
    down: false,
    sprint: false,
  })

  const velocity = useRef<VelocityState>({
    forward: 0,
    right: 0,
    vertical: 0,
  })

  // Keyboard input handler
  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.code) {
        case 'KeyW':
        case 'ArrowUp':
          keysPressed.current.forward = true
          break
        case 'KeyS':
        case 'ArrowDown':
          keysPressed.current.backward = true
          break
        case 'KeyA':
        case 'ArrowLeft':
          keysPressed.current.left = true
          break
        case 'KeyD':
        case 'ArrowRight':
          keysPressed.current.right = true
          break
        case 'Space':
          e.preventDefault()
          keysPressed.current.up = true
          break
        case 'ControlLeft':
        case 'ControlRight':
          e.preventDefault()
          keysPressed.current.down = true
          break
        case 'ShiftLeft':
        case 'ShiftRight':
          keysPressed.current.sprint = true
          break
      }
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      switch (e.code) {
        case 'KeyW':
        case 'ArrowUp':
          keysPressed.current.forward = false
          break
        case 'KeyS':
        case 'ArrowDown':
          keysPressed.current.backward = false
          break
        case 'KeyA':
        case 'ArrowLeft':
          keysPressed.current.left = false
          break
        case 'KeyD':
        case 'ArrowRight':
          keysPressed.current.right = false
          break
        case 'Space':
          keysPressed.current.up = false
          break
        case 'ControlLeft':
        case 'ControlRight':
          keysPressed.current.down = false
          break
        case 'ShiftLeft':
        case 'ShiftRight':
          keysPressed.current.sprint = false
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [enabled])

  // Movement physics with smooth acceleration and collision detection
  useFrame((state, delta) => {
    if (!enabled) return

    const actualSpeed = speed * (keysPressed.current.sprint ? 2 : 1)
    const accel = acceleration * delta
    const decel = deceleration * delta

    // Smooth acceleration/deceleration for forward/backward
    if (keysPressed.current.forward) {
      velocity.current.forward = Math.min(velocity.current.forward + accel, 1)
    } else if (keysPressed.current.backward) {
      velocity.current.forward = Math.max(velocity.current.forward - accel, -1)
    } else {
      // Decelerate to zero
      if (velocity.current.forward > 0) {
        velocity.current.forward = Math.max(0, velocity.current.forward - decel)
      } else if (velocity.current.forward < 0) {
        velocity.current.forward = Math.min(0, velocity.current.forward + decel)
      }
    }

    // Smooth acceleration/deceleration for left/right
    if (keysPressed.current.right) {
      velocity.current.right = Math.min(velocity.current.right + accel, 1)
    } else if (keysPressed.current.left) {
      velocity.current.right = Math.max(velocity.current.right - accel, -1)
    } else {
      // Decelerate to zero
      if (velocity.current.right > 0) {
        velocity.current.right = Math.max(0, velocity.current.right - decel)
      } else if (velocity.current.right < 0) {
        velocity.current.right = Math.min(0, velocity.current.right + decel)
      }
    }

    // Smooth acceleration/deceleration for vertical
    if (keysPressed.current.up) {
      velocity.current.vertical = Math.min(velocity.current.vertical + accel, 1)
    } else if (keysPressed.current.down) {
      velocity.current.vertical = Math.max(velocity.current.vertical - accel, -1)
    } else {
      // Decelerate to zero
      if (velocity.current.vertical > 0) {
        velocity.current.vertical = Math.max(0, velocity.current.vertical - decel)
      } else if (velocity.current.vertical < 0) {
        velocity.current.vertical = Math.min(0, velocity.current.vertical + decel)
      }
    }

    // Get camera direction (forward vector)
    const direction = new THREE.Vector3()
    camera.getWorldDirection(direction)
    direction.y = 0 // Keep movement horizontal
    direction.normalize()

    // Get right vector (perpendicular to forward)
    const right = new THREE.Vector3()
    right.crossVectors(camera.up, direction).normalize()

    // Calculate desired movement
    const moveVector = new THREE.Vector3()
    moveVector.addScaledVector(direction, velocity.current.forward * actualSpeed * delta)
    moveVector.addScaledVector(right, velocity.current.right * actualSpeed * delta)
    moveVector.y = velocity.current.vertical * actualSpeed * delta

    // Apply collision detection if octree is available
    if (octree && (velocity.current.forward !== 0 || velocity.current.right !== 0 || velocity.current.vertical !== 0)) {
      const newPosition = camera.position.clone().add(moveVector)
      
      // Check for nearby points
      const nearbyPoints = octree.findPointsInSphere(newPosition, collisionRadius)
      
      if (nearbyPoints.length === 0) {
        // No collision, move freely
        camera.position.copy(newPosition)
      } else {
        // Collision detected - slide along the surface
        // Find average collision normal
        const collisionNormal = new THREE.Vector3()
        for (const point of nearbyPoints) {
          const toCamera = newPosition.clone().sub(point).normalize()
          collisionNormal.add(toCamera)
        }
        collisionNormal.normalize()
        
        // Project movement vector along the collision surface
        const dot = moveVector.dot(collisionNormal)
        if (dot < 0) {
          // Only slide if moving toward the collision
          moveVector.addScaledVector(collisionNormal, -dot)
        }
        
        // Apply adjusted movement
        const adjustedPosition = camera.position.clone().add(moveVector)
        
        // Final check - ensure we're not inside geometry
        const finalCheck = octree.findPointsInSphere(adjustedPosition, collisionRadius * 0.8)
        if (finalCheck.length === 0) {
          camera.position.copy(adjustedPosition)
        } else {
          // Push out of geometry
          camera.position.addScaledVector(collisionNormal, collisionRadius * 0.1)
        }
      }
    } else {
      // No octree - move without collision detection
      camera.position.add(moveVector)
    }
  })

  return null
}

// ==================== POINT CLOUD LOADER ====================

interface PointCloudProps {
  url: string
  onLoad?: (geometry: THREE.BufferGeometry) => void
  onPointCount?: (count: number) => void
}

function PointCloud({ url, onLoad, onPointCount }: PointCloudProps) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)
  const pointsRef = useRef<THREE.Points>(null)
  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('desktop')
  
  useEffect(() => {
    // Only run on client side
    if (typeof window !== 'undefined') {
      setDeviceType(getDeviceType())
    }
  }, [])
  
  const pointSize = useMemo(() => getPointSize(deviceType), [deviceType])

  useEffect(() => {
    let mounted = true
    const loader = new PLYLoader()
    
    loader.load(
      url,
      (loadedGeometry) => {
        if (!mounted) {
          loadedGeometry.dispose()
          return
        }

        loadedGeometry.computeBoundingBox()
        loadedGeometry.computeBoundingSphere()

        // Align to Z=0 base
        if (loadedGeometry.boundingBox) {
          const minZ = loadedGeometry.boundingBox.min.z
          const positions = loadedGeometry.getAttribute('position')
          for (let i = 0; i < positions.count; i++) {
            positions.setZ(i, positions.getZ(i) - minZ)
          }
          positions.needsUpdate = true
          loadedGeometry.computeBoundingBox()
        }

        const count = loadedGeometry.getAttribute('position').count
        onPointCount?.(count)

        // Get optimal point cloud size for device
        const optimalSize = getOptimalPointCloudSize(count)
        const needsDownsampling = count > optimalSize

        if (needsDownsampling) {
          const deviceName = deviceType === 'mobile' ? '📱 Mobile' : deviceType === 'tablet' ? '📱 Tablet' : '💻 Desktop'
          console.log(`${deviceName} detected - Optimizing point cloud...`)
          console.log(`⚡ ${(count / 1_000_000).toFixed(1)}M → ${(optimalSize / 1_000_000).toFixed(1)}M points`)
          
          const downsampleFactor = Math.ceil(count / optimalSize)
          const positions = loadedGeometry.getAttribute('position')
          const colors = loadedGeometry.getAttribute('color')
          
          const newPositions = []
          const newColors = []
          
          for (let i = 0; i < positions.count; i += downsampleFactor) {
            newPositions.push(positions.getX(i), positions.getY(i), positions.getZ(i))
            if (colors) {
              newColors.push(colors.getX(i), colors.getY(i), colors.getZ(i))
            }
          }
          
          const optimizedGeometry = new THREE.BufferGeometry()
          optimizedGeometry.setAttribute('position', new THREE.Float32BufferAttribute(newPositions, 3))
          if (newColors.length > 0) {
            optimizedGeometry.setAttribute('color', new THREE.Float32BufferAttribute(newColors, 3))
          }
          optimizedGeometry.computeBoundingBox()
          optimizedGeometry.computeBoundingSphere()
          
          // Dispose original geometry to free memory
          loadedGeometry.dispose()
          
          console.log(`✅ Optimized for ${deviceType}`)
          
          if (mounted) {
            setGeometry(optimizedGeometry)
            onLoad?.(optimizedGeometry)
          } else {
            optimizedGeometry.dispose()
          }
        } else {
          if (mounted) {
            setGeometry(loadedGeometry)
            onLoad?.(loadedGeometry)
          } else {
            loadedGeometry.dispose()
          }
        }
      },
      (progress) => {
        const percent = (progress.loaded / progress.total) * 100
        if (percent % 20 === 0) {
          console.log(`Loading point cloud: ${percent.toFixed(0)}%`)
        }
      },
      (error) => {
        console.error('Error loading PLY:', error)
      }
    )

    return () => {
      mounted = false
      // Cleanup geometry on unmount
      if (geometry) {
        geometry.dispose()
      }
    }
  }, [url, deviceType])

  if (!geometry) return null

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={pointSize}
        vertexColors
        sizeAttenuation
        transparent
        opacity={0.95}
        depthWrite={false}
      />
    </points>
  )
}

// ==================== POSITION HUD TRACKER ====================

interface PositionHUDTrackerProps {
  onUpdate: (position: THREE.Vector3, rotation: THREE.Euler) => void
}

function PositionHUDTracker({ onUpdate }: PositionHUDTrackerProps) {
  const { camera } = useThree()

  useFrame(() => {
    onUpdate(camera.position, camera.rotation)
  })

  return null
}

// ==================== MAIN SCENE CONTENT ====================

interface SceneContentProps {
  plyUrl: string
  speed: number
  controlsEnabled: boolean
  onGeometryLoad: (geometry: THREE.BufferGeometry) => void
  onPointCount: (count: number) => void
  onPositionUpdate: (position: THREE.Vector3, rotation: THREE.Euler) => void
  octree: Octree | null
}

function SceneContent({ 
  plyUrl, 
  speed, 
  controlsEnabled, 
  onGeometryLoad, 
  onPointCount,
  onPositionUpdate,
  octree
}: SceneContentProps) {
  const controlsRef = useRef<any>()

  return (
    <>
      {/* Lights */}
      <ambientLight intensity={0.8} />
      <directionalLight position={[10, 10, 10]} intensity={0.5} />

      {/* Point Cloud */}
      <PointCloud 
        url={plyUrl} 
        onLoad={onGeometryLoad}
        onPointCount={onPointCount}
      />

      {/* Grid Helper */}
      <gridHelper args={[100, 100, '#3E93C9', '#1a1a1a']} />

      {/* First Person Controller with Collision Detection */}
      <FirstPersonController 
        speed={speed} 
        enabled={controlsEnabled}
        octree={octree}
        collisionRadius={0.3}
        acceleration={8}
        deceleration={10}
      />

      {/* Pointer Lock Controls for Mouse Look */}
      <PointerLockControls ref={controlsRef} />

      {/* Position Tracker */}
      <PositionHUDTracker onUpdate={onPositionUpdate} />
    </>
  )
}

// ==================== UI COMPONENTS ====================

interface PositionHUDProps {
  position: THREE.Vector3
  rotation: THREE.Euler
  visible: boolean
}

function PositionHUD({ position, rotation, visible }: PositionHUDProps) {
  if (!visible) return null

  const pitch = THREE.MathUtils.radToDeg(rotation.x)
  const yaw = THREE.MathUtils.radToDeg(rotation.y)

  return (
    <div className="absolute bottom-4 left-4 bg-surface-elevated/90 backdrop-blur-sm border border-app-primary rounded-lg px-4 py-3 font-mono text-xs space-y-1.5 shadow-lg">
      <div className="text-primary-400 font-semibold mb-2 flex items-center gap-2">
        <Eye className="w-3.5 h-3.5" />
        Camera Position
      </div>
      <div className="grid grid-cols-2 gap-x-3 gap-y-1">
        <span className="text-gray-400">X:</span>
        <span className="text-white tabular-nums">{position.x.toFixed(2)}</span>
        <span className="text-gray-400">Y:</span>
        <span className="text-white tabular-nums">{position.y.toFixed(2)}</span>
        <span className="text-gray-400">Z:</span>
        <span className="text-white tabular-nums">{position.z.toFixed(2)}</span>
        <span className="text-gray-400">Pitch:</span>
        <span className="text-white tabular-nums">{pitch.toFixed(1)}°</span>
        <span className="text-gray-400">Yaw:</span>
        <span className="text-white tabular-nums">{yaw.toFixed(1)}°</span>
      </div>
    </div>
  )
}

interface ControlsHelpProps {
  visible: boolean
  onClose: () => void
}

function ControlsHelp({ visible, onClose }: ControlsHelpProps) {
  if (!visible) return null

  return (
    <div className="absolute top-4 right-4 bg-surface-elevated/95 backdrop-blur-sm border border-app-primary rounded-lg p-4 shadow-xl max-w-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-primary-400 font-semibold flex items-center gap-2">
          <Info className="w-4 h-4" />
          First Person Controls
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      
      <div className="space-y-3 text-sm">
        <div>
          <div className="text-white font-medium mb-1.5">Movement</div>
          <div className="space-y-1 text-gray-300">
            <div className="flex items-center gap-2">
              <kbd className="px-2 py-0.5 bg-surface-tertiary border border-app-primary rounded text-xs">W A S D</kbd>
              <span>Move forward/left/back/right</span>
            </div>
            <div className="flex items-center gap-2">
              <kbd className="px-2 py-0.5 bg-surface-tertiary border border-app-primary rounded text-xs">Space</kbd>
              <span>Move up</span>
            </div>
            <div className="flex items-center gap-2">
              <kbd className="px-2 py-0.5 bg-surface-tertiary border border-app-primary rounded text-xs">Ctrl</kbd>
              <span>Move down</span>
            </div>
            <div className="flex items-center gap-2">
              <kbd className="px-2 py-0.5 bg-surface-tertiary border border-app-primary rounded text-xs">Shift</kbd>
              <span>Sprint (2× speed)</span>
            </div>
          </div>
        </div>
        
        <div>
          <div className="text-white font-medium mb-1.5">Camera</div>
          <div className="space-y-1 text-gray-300">
            <div className="flex items-center gap-2">
              <MousePointer2 className="w-3.5 h-3.5" />
              <span>Move mouse to look around</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                (Click canvas to lock pointer)
              </span>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-app-secondary">
          <div className="text-xs text-gray-400">
            ✨ <span className="text-primary-400">Collision detection enabled</span> - you won't walk through walls!
          </div>
        </div>
      </div>
    </div>
  )
}

// ==================== MAIN COMPONENT ====================

export default function FirstPersonViewer({
  plyUrl,
  scanId,
  initialSpeed = 3,
  initialPosition = [0, 1.6, 5],
  onPositionChange,
  onRotationChange,
  className = "",
  showStats = false,
}: FirstPersonViewerProps) {
  const [speed, setSpeed] = useState(initialSpeed)
  const [controlsEnabled, setControlsEnabled] = useState(true)
  const [showHelp, setShowHelp] = useState(true)
  const [showHUD, setShowHUD] = useState(true)
  const [currentPosition, setCurrentPosition] = useState(new THREE.Vector3(...initialPosition))
  const [currentRotation, setCurrentRotation] = useState(new THREE.Euler())
  const [pointCount, setPointCount] = useState(0)
  const [octree, setOctree] = useState<Octree | null>(null)
  const [octreeStats, setOctreeStats] = useState<{ nodes: number; points: number; maxDepth: number } | null>(null)

  const handlePositionUpdate = useCallback((position: THREE.Vector3, rotation: THREE.Euler) => {
    setCurrentPosition(position.clone())
    setCurrentRotation(rotation.clone())
    onPositionChange?.(position)
    onRotationChange?.({
      pitch: THREE.MathUtils.radToDeg(rotation.x),
      yaw: THREE.MathUtils.radToDeg(rotation.y),
    })
  }, [onPositionChange, onRotationChange])

  const handleGeometryLoad = useCallback((geometry: THREE.BufferGeometry) => {
    // Check if collision should be enabled for this device
    if (typeof window !== 'undefined' && !shouldEnableCollision()) {
      console.log('📱 Mobile device - Collision detection disabled for performance')
      return
    }

    console.log('🌳 Building octree for collision detection...')
    const start = performance.now()
    
    // Build octree asynchronously to avoid blocking
    setTimeout(() => {
      try {
        const tree = Octree.fromGeometry(geometry)
        const stats = tree.getStats()
        const elapsed = performance.now() - start
        
        console.log(`✅ Octree built in ${elapsed.toFixed(0)}ms`)
        console.log(`   - Nodes: ${stats.nodes.toLocaleString()}`)
        console.log(`   - Points: ${stats.points.toLocaleString()}`)
        console.log(`   - Max Depth: ${stats.maxDepth}`)
        
        setOctree(tree)
        setOctreeStats(stats)
      } catch (error) {
        console.error('❌ Failed to build octree:', error)
        console.log('⚠️ Collision detection disabled')
      }
    }, 100)
  }, [])

  const handleReset = () => {
    setCurrentPosition(new THREE.Vector3(...initialPosition))
    setSpeed(initialSpeed)
  }

  // WebGL context lost/restored handlers
  useEffect(() => {
    const handleContextLost = (event: Event) => {
      event.preventDefault()
      console.error('⚠️ WebGL context lost! Attempting to restore...')
    }

    const handleContextRestored = () => {
      console.log('✅ WebGL context restored')
      // Force reload of geometry
      window.location.reload()
    }

    const canvas = document.querySelector('canvas')
    if (canvas) {
      canvas.addEventListener('webglcontextlost', handleContextLost)
      canvas.addEventListener('webglcontextrestored', handleContextRestored)

      return () => {
        canvas.removeEventListener('webglcontextlost', handleContextLost)
        canvas.removeEventListener('webglcontextrestored', handleContextRestored)
      }
    }
  }, [])

  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('desktop')
  
  useEffect(() => {
    // Only run on client side
    setDeviceType(getDeviceType())
  }, [])
  
  const canvasConfig = useMemo(() => getCanvasConfig(deviceType), [deviceType])

  return (
    <div className={`relative w-full h-full bg-app-primary ${className}`}>
      {/* 3D Canvas */}
      <Canvas
        camera={{
          position: initialPosition,
          fov: 75,
          near: 0.1,
          far: 1000,
        }}
        className="w-full h-full"
        dpr={canvasConfig.pixelRatio}
        gl={{
          antialias: canvasConfig.antialias,
          powerPreference: canvasConfig.powerPreference,
          preserveDrawingBuffer: canvasConfig.preserveDrawingBuffer,
          failIfMajorPerformanceCaveat: false, // Don't fail on low-end devices
        }}
        onCreated={({ gl }) => {
          console.log('✅ WebGL Context Created:', {
            renderer: gl.capabilities.renderer,
            maxTextures: gl.capabilities.maxTextures,
            maxVertexAttributes: gl.capabilities.maxVertexAttributes,
          })
        }}
      >
        <SceneContent
          plyUrl={plyUrl}
          speed={speed}
          controlsEnabled={controlsEnabled}
          onGeometryLoad={handleGeometryLoad}
          onPointCount={setPointCount}
          onPositionUpdate={handlePositionUpdate}
          octree={octree}
        />
        {showStats && <Stats />}
      </Canvas>

      {/* Crosshair */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="relative w-6 h-6">
          <div className="absolute left-1/2 top-1/2 w-0.5 h-3 bg-primary-400 -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute left-1/2 top-1/2 w-3 h-0.5 bg-primary-400 -translate-x-1/2 -translate-y-1/2" />
        </div>
      </div>

      {/* Position HUD */}
      <PositionHUD
        position={currentPosition}
        rotation={currentRotation}
        visible={showHUD}
      />

      {/* Controls Help */}
      <ControlsHelp visible={showHelp} onClose={() => setShowHelp(false)} />

      {/* Top Bar UI */}
      <div className="absolute top-4 left-4 flex items-center gap-2 md:gap-3">
        <button
          onClick={() => setShowHelp(!showHelp)}
          className="bg-surface-elevated/90 backdrop-blur-sm hover:bg-surface-elevated border border-app-primary text-white p-2 md:p-2.5 rounded-lg transition-all shadow-lg hover:border-primary-400 active:scale-95"
          title="Toggle Help"
        >
          <Info className="w-5 h-5 md:w-4 md:h-4" />
        </button>

        <button
          onClick={() => setShowHUD(!showHUD)}
          className="bg-surface-elevated/90 backdrop-blur-sm hover:bg-surface-elevated border border-app-primary text-white p-2 md:p-2.5 rounded-lg transition-all shadow-lg hover:border-primary-400 active:scale-95"
          title="Toggle HUD"
        >
          {showHUD ? <Eye className="w-5 h-5 md:w-4 md:h-4" /> : <EyeOff className="w-5 h-5 md:w-4 md:h-4" />}
        </button>

        <button
          onClick={handleReset}
          className="bg-surface-elevated/90 backdrop-blur-sm hover:bg-surface-elevated border border-app-primary text-white p-2 md:p-2.5 rounded-lg transition-all shadow-lg hover:border-primary-400 active:scale-95"
          title="Reset Position"
        >
          <RotateCcw className="w-5 h-5 md:w-4 md:h-4" />
        </button>

        {/* Point Count Badge - Hide text on mobile */}
        {pointCount > 0 && (
          <div className="bg-surface-elevated/90 backdrop-blur-sm border border-app-primary px-2 md:px-3 py-1.5 md:py-2 rounded-lg text-xs font-mono shadow-lg">
            <span className="text-gray-400 hidden md:inline">Points: </span>
            <span className="text-primary-400 font-semibold">
              {(pointCount / 1_000_000).toFixed(1)}M
            </span>
          </div>
        )}

        {/* Octree Stats Badge - Hide on mobile */}
        {octreeStats && (
          <div className="hidden md:block bg-surface-elevated/90 backdrop-blur-sm border border-app-primary px-3 py-2 rounded-lg text-xs font-mono shadow-lg">
            <span className="text-gray-400">Octree:</span>{' '}
            <span className="text-green-400 font-semibold">
              {octreeStats.nodes.toLocaleString()} nodes
            </span>
          </div>
        )}
      </div>

      {/* Bottom Controls - Responsive for mobile */}
      <div className="absolute bottom-4 right-4 bg-surface-elevated/90 backdrop-blur-sm border border-app-primary rounded-lg p-3 md:p-4 shadow-xl">
        <div className="flex items-center gap-2 md:gap-3">
          <Gauge className="w-5 h-5 md:w-4 md:h-4 text-primary-400" />
          <div className="flex flex-col gap-1.5 md:gap-1">
            <div className="flex items-center justify-between gap-3 md:gap-4">
              <span className="text-xs text-gray-400">Speed</span>
              <span className="text-xs md:text-xs font-mono text-white tabular-nums">{speed.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="10"
              step="0.5"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-24 md:w-32 h-2 accent-primary-400"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
