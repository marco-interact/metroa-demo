'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { SplineLoader } from '@/components/ui/spline-loader'

export default function HomePage() {
  const router = useRouter()
  
  useEffect(() => {
    // Client-side redirect to dashboard
    router.push('/dashboard')
  }, [router])
  
  return (
    <div className="min-h-screen bg-app-primary flex items-center justify-center">
      <div className="w-full h-full max-w-4xl max-h-[600px]">
        <SplineLoader className="rounded-lg overflow-hidden" />
      </div>
    </div>
  )
}