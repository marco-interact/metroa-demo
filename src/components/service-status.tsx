"use client"

import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Activity } from 'lucide-react'
import { apiClient, isDemoMode } from '@/lib/api'

export function ServiceStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null)
  const [isDemo, setIsDemo] = useState(false)

  useEffect(() => {
    const checkConnection = async () => {
      setIsDemo(isDemoMode())
      
      if (isDemoMode()) {
        setIsConnected(true) // Demo mode is always "connected"
        return
      }

      try {
        console.log('🔍 Checking backend health...')
        const health = await apiClient.healthCheck()
        console.log('✅ Health check response:', health)
        setIsConnected(health.status === 'healthy' || health.status === 'running')
      } catch (error) {
        console.error('❌ Health check failed:', error)
        setIsConnected(false)
      }
    }

    checkConnection()
    
    // Check every 10 seconds (more frequent for faster feedback)
    const interval = setInterval(checkConnection, 10000)
    return () => clearInterval(interval)
  }, [])

  if (isConnected === null) {
    return (
      <div className="flex items-center text-gray-400">
        <Activity className="w-4 h-4 mr-1 animate-pulse" />
        <span className="text-xs">Checking...</span>
      </div>
    )
  }

  if (isDemo) {
    return (
      <div className="flex items-center text-blue-400">
        <div className="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse" />
        <span className="text-xs font-medium">Demo Mode</span>
      </div>
    )
  }

  return (
    <div className={`flex items-center ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
      {isConnected ? (
        <Wifi className="w-4 h-4 mr-1" />
      ) : (
        <WifiOff className="w-4 h-4 mr-1" />
      )}
      <span className="text-xs font-medium">
        {isConnected ? 'Connected' : 'Offline'}
      </span>
    </div>
  )
}
