"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { PointerLockControls, Stats } from "@react-three/drei"
import * as THREE from "three"
import { PLYLoader } from "three-stdlib"
import { RotateCcw, Maximize2, Minimize2, Eye, EyeOff, Info, X } from "lucide-react"

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
  minPolarAngle?: number
  maxPolarAngle?: number
}

type ControlMode = 'orbit' | 'firstperson'

interface KeyboardState {
  forward: boolean
  backward: boolean
  left: boolean
  right: boolean
  up: boolean
  down: boolean
  sprint: boolean
}

// ==================== FIRST PERSON CONTROLLER ====================

function FirstPersonController({ speed, enabled }: FirstPersonControllerProps) {
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

  // Movement physics in animation loop
  useFrame((state, delta) => {
    if (!enabled) return

    const actualSpeed = speed * (keysPressed.current.sprint ? 2 : 1)
    const moveDistance = actualSpeed * delta

    // Get camera direction (forward vector)
    const direction = new THREE.Vector3()
    camera.getWorldDirection(direction)
    direction.y = 0 // Keep movement horizontal
    direction.normalize()

    // Get right vector (perpendicular to forward)
    const right = new THREE.Vector3()
    right.crossVectors(camera.up, direction).normalize()

    // Apply movement
    if (keysPressed.current.forward) {
      camera.position.addScaledVector(direction, moveDistance)
    }
    if (keysPressed.current.backward) {
      camera.position.addScaledVector(direction, -moveDistance)
    }
    if (keysPressed.current.right) {
      camera.position.addScaledVector(right, moveDistance)
    }
    if (keysPressed.current.left) {
      camera.position.addScaledVector(right, -moveDistance)
    }
    if (keysPressed.current.up) {
      camera.position.y += moveDistance
    }
    if (keysPressed.current.down) {
      camera.position.y -= moveDistance
    }
  })

  return null
}

// ==================== POINT CLOUD WITH OPTIMIZATION ====================

function OptimizedPointCloud({ url }: { url: string }) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!url) return

    setLoading(true)
    setError(null)

    const loader = new PLYLoader()

    loader.load(
      url,
      (loadedGeometry) => {
        loadedGeometry.computeBoundingBox()
        loadedGeometry.computeBoundingSphere()

        // Optimize: Downsample if > 5M points for smooth 60fps
        const posCount = loadedGeometry.getAttribute('position').count
        
        if (posCount > 5_000_000) {
          console.log(`🔄 Downsampling ${posCount.toLocaleString()} points to 5M for performance...`)
          const decimated = decimatePointCloud(loadedGeometry, 5_000_000)
          setGeometry(decimated)
        } else {
          setGeometry(loadedGeometry)
        }

        setLoading(false)
        console.log(`✅ Point cloud loaded: ${posCount.toLocaleString()} points`)
      },
      (progress) => {
        if (progress.total > 0) {
          const percent = (progress.loaded / progress.total) * 100
          if (percent % 20 < 1) {
            console.log(`Loading: ${percent.toFixed(0)}%`)
          }
        }
      },
      (err) => {
        console.error('❌ Error loading PLY:', err)
        setError('Failed to load 3D model')
        setLoading(false)
      }
    )
  }, [url])

  if (loading || !geometry) return null
  if (error) return null

  return (
    <points geometry={geometry}>
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

// Downsample point cloud using random sampling
function decimatePointCloud(
  geo: THREE.BufferGeometry,
  targetCount: number
): THREE.BufferGeometry {
  const positions = geo.getAttribute('position')
  const colors = geo.getAttribute('color')
  const ratio = targetCount / positions.count

  const newPos: number[] = []
  const newCol: number[] = []

  for (let i = 0; i < positions.count; i++) {
    if (Math.random() < ratio) {
      newPos.push(positions.getX(i), positions.getY(i), positions.getZ(i))
      if (colors) {
        newCol.push(colors.getX(i), colors.getY(i), colors.getZ(i))
      }
    }
  }

  const newGeo = new THREE.BufferGeometry()
  newGeo.setAttribute('position', new THREE.Float32BufferAttribute(newPos, 3))
  if (newCol.length) {
    newGeo.setAttribute('color', new THREE.Float32BufferAttribute(newCol, 3))
  }

  return newGeo
}

// ==================== CROSSHAIR OVERLAY ====================

function Crosshair({ visible }: { visible: boolean }) {
  if (!visible) return null

  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-20">
      <div className="relative">
        {/* Horizontal line */}
        <div className="absolute w-8 h-0.5 bg-white/70 left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
        {/* Vertical line */}
        <div className="absolute w-0.5 h-8 bg-white/70 left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
        {/* Center dot */}
        <div className="absolute w-1.5 h-1.5 bg-white/90 rounded-full left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
      </div>
    </div>
  )
}

// ==================== POINTER LOCK PROMPT ====================

function PointerLockPrompt({ visible }: { visible: boolean }) {
  if (!visible) return null

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-10 pointer-events-none">
      <div className="bg-app-elevated/95 border border-app-secondary p-8 rounded-lg shadow-2xl pointer-events-auto text-center max-w-md">
        <div className="text-6xl mb-4">🎮</div>
        <h3 className="text-white text-xl font-bold mb-2">First-Person Mode</h3>
        <p className="text-gray-300 mb-4">Click anywhere to enable mouse look</p>
        <p className="text-gray-500 text-sm">Press <kbd className="px-2 py-1 bg-gray-700 rounded">ESC</kbd> to exit</p>
      </div>
    </div>
  )
}

// ==================== CONTROLS HELP PANEL ====================

function ControlsHelp({ onClose }: { onClose: () => void }) {
  return (
    <div className="absolute top-4 left-4 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary p-4 rounded-lg text-white text-sm max-w-xs z-30">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-base flex items-center gap-2">
          <Info className="w-4 h-4" />
          Controls
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Move Forward</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">W</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Move Backward</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">S</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Strafe Left</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">A</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Strafe Right</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">D</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Move Up</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">Space</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Move Down</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">Ctrl</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Sprint (2x)</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">Shift</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Look Around</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">Mouse</kbd>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Exit Mouse Look</span>
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-xs">ESC</kbd>
        </div>
      </div>
    </div>
  )
}

// ==================== POSITION HUD DATA TRACKER ====================

// This component runs inside Canvas and tracks camera data
function PositionHUDTracker({ onUpdate }: { onUpdate: (data: any) => void }) {
  const { camera } = useThree()

  useFrame(() => {
    // Get position
    const position = {
      x: camera.position.x,
      y: camera.position.y,
      z: camera.position.z,
    }

    // Calculate pitch and yaw from camera rotation
    const direction = new THREE.Vector3()
    camera.getWorldDirection(direction)
    
    const pitch = Math.asin(-direction.y) * (180 / Math.PI)
    const yaw = Math.atan2(direction.x, direction.z) * (180 / Math.PI)

    onUpdate({ position, rotation: { pitch, yaw } })
  })

  return null
}

// ==================== POSITION HUD DISPLAY ====================

// This component displays the HUD (outside Canvas)
function PositionHUD({ position, rotation }: { 
  position: { x: number; y: number; z: number }
  rotation: { pitch: number; yaw: number }
}) {
  return (
    <div className="absolute bottom-4 left-4 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary px-4 py-2 rounded-lg font-mono text-xs text-white z-30">
      <div className="flex items-center gap-3">
        <div>
          <span className="text-gray-400">Pos:</span>{' '}
          <span className="text-green-400">
            {position.x.toFixed(2)}, {position.y.toFixed(2)}, {position.z.toFixed(2)}
          </span>
        </div>
        <div className="text-gray-600">|</div>
        <div>
          <span className="text-gray-400">Pitch:</span>{' '}
          <span className="text-blue-400">{rotation.pitch.toFixed(1)}°</span>
        </div>
        <div>
          <span className="text-gray-400">Yaw:</span>{' '}
          <span className="text-purple-400">{rotation.yaw.toFixed(1)}°</span>
        </div>
      </div>
    </div>
  )
}

// ==================== SPEED CONTROL ====================

function SpeedControl({
  speed,
  onSpeedChange,
}: {
  speed: number
  onSpeedChange: (speed: number) => void
}) {
  return (
    <div className="absolute bottom-4 right-4 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary p-3 rounded-lg z-30">
      <label className="flex items-center gap-3 text-white text-sm">
        <span className="text-gray-400">Speed:</span>
        <input
          type="range"
          min="1"
          max="20"
          step="0.5"
          value={speed}
          onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
          className="w-32 accent-blue-500"
        />
        <span className="w-12 text-right font-mono text-green-400">{speed.toFixed(1)}</span>
        <span className="text-gray-500 text-xs">m/s</span>
      </label>
    </div>
  )
}

// ==================== MODE TOGGLE BUTTON ====================

function ModeToggle({
  mode,
  onModeChange,
}: {
  mode: ControlMode
  onModeChange: (mode: ControlMode) => void
}) {
  return (
    <div className="absolute top-4 right-4 z-30">
      <button
        onClick={() => onModeChange(mode === 'orbit' ? 'firstperson' : 'orbit')}
        className="flex items-center gap-2 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary hover:border-blue-500 px-4 py-2 rounded-lg text-white text-sm font-medium transition-all hover:bg-app-elevated"
        title={mode === 'firstperson' ? 'Switch to Orbit View' : 'Switch to First-Person View'}
      >
        {mode === 'firstperson' ? (
          <>
            <Eye className="w-4 h-4" />
            <span>First Person</span>
          </>
        ) : (
          <>
            <RotateCcw className="w-4 h-4" />
            <span>Orbit View</span>
          </>
        )}
      </button>
    </div>
  )
}

// ==================== MAIN COMPONENT ====================

export function FirstPersonViewer({
  plyUrl,
  scanId,
  initialSpeed = 5.0,
  initialPosition = [0, 1.6, 5],
  className = "",
  showStats = false,
}: FirstPersonViewerProps) {
  const [mode, setMode] = useState<ControlMode>('firstperson')
  const [speed, setSpeed] = useState(initialSpeed)
  const [isLocked, setIsLocked] = useState(false)
  const [showHelp, setShowHelp] = useState(true)
  const [cameraData, setCameraData] = useState({
    position: { x: 0, y: 1.6, z: 5 },
    rotation: { pitch: 0, yaw: 0 }
  })

  return (
    <div className={`relative bg-app-card rounded-lg overflow-hidden ${className}`}>
      {/* 3D Canvas */}
      <Canvas
        camera={{
          position: initialPosition,
          fov: 75,
        }}
        className="bg-app-card"
        gl={{
          antialias: true,
          powerPreference: "high-performance",
          preserveDrawingBuffer: true,
        }}
        dpr={[1, 2]}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <directionalLight position={[-10, -10, -10]} intensity={0.3} />

        {/* Grid helper */}
        <gridHelper args={[50, 50, '#444444', '#222222']} />

        {/* Controls - Conditional based on mode */}
        {mode === 'firstperson' ? (
          <>
            <PointerLockControls
              makeDefault
              onLock={() => setIsLocked(true)}
              onUnlock={() => setIsLocked(false)}
            />
            <FirstPersonController speed={speed} enabled={mode === 'firstperson'} />
          </>
        ) : (
          <></>
        )}

        {/* Point Cloud */}
        <OptimizedPointCloud url={plyUrl} />

        {/* Position HUD data tracker (inside Canvas) */}
        <PositionHUDTracker onUpdate={setCameraData} />

        {/* Stats (FPS counter) */}
        {showStats && <Stats />}
      </Canvas>

      {/* UI Overlays */}
      <Crosshair visible={mode === 'firstperson' && isLocked} />
      <PointerLockPrompt visible={mode === 'firstperson' && !isLocked} />
      
      {showHelp && mode === 'firstperson' && (
        <ControlsHelp onClose={() => setShowHelp(false)} />
      )}

      <PositionHUD position={cameraData.position} rotation={cameraData.rotation} />
      <SpeedControl speed={speed} onSpeedChange={setSpeed} />
      <ModeToggle mode={mode} onModeChange={setMode} />

      {/* Help button to re-show controls */}
      {!showHelp && mode === 'firstperson' && (
        <button
          onClick={() => setShowHelp(true)}
          className="absolute top-4 left-4 bg-app-elevated/95 backdrop-blur-sm border border-app-secondary hover:border-blue-500 p-2 rounded-lg text-white transition-all z-30"
          title="Show controls"
        >
          <Info className="w-4 h-4" />
        </button>
      )}

      {/* Status indicator */}
      <div className="absolute top-20 right-4 z-30">
        <div className="bg-app-elevated/95 backdrop-blur-sm border border-app-secondary px-3 py-1.5 rounded-lg flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isLocked ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-white text-xs font-medium">
            {isLocked ? 'Mouse Locked' : 'Click to Lock'}
          </span>
        </div>
      </div>
    </div>
  )
}


