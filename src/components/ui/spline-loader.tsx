"use client"

import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// Dynamically import Spline to avoid SSR issues
// Note: @splinetool/react-spline exports Spline as default
const Spline = dynamic(
  () => import('@splinetool/react-spline'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }
)

interface SplineLoaderProps {
  className?: string
  scene?: string
  style?: React.CSSProperties
}

export function SplineLoader({ 
  className = "",
  scene = "https://prod.spline.design/EbRg3AA-HXokBWoZ/scene.splinecode",
  style
}: SplineLoaderProps) {
  return (
    <div className={`w-full h-full ${className}`} style={style}>
      <Suspense fallback={
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      }>
        <Spline scene={scene} />
      </Suspense>
    </div>
  )
}

