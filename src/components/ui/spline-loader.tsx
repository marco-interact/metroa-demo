"use client"

// Simple spinner loader (Spline integration temporarily disabled due to package export issues)
// TODO: Re-enable Spline when @splinetool/react-spline package exports are fixed

interface SplineLoaderProps {
  className?: string
  scene?: string
  style?: React.CSSProperties
}

export function SplineLoader({ 
  className = "",
  scene,
  style
}: SplineLoaderProps) {
  // Return elegant spinner loader
  return (
    <div className={`w-full h-full ${className}`} style={style}>
      <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-primary-900/20 to-primary-800/10">
        <div className="relative">
          {/* Outer spinning ring */}
          <div className="w-20 h-20 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          {/* Inner pulsing dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse"></div>
          </div>
        </div>
        <p className="mt-4 text-sm text-gray-400 font-mono">Loading...</p>
      </div>
    </div>
  )
}

