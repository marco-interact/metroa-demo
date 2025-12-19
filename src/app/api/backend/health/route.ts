import { NextResponse } from 'next/server'

// Backend URL - use environment variable or fallback
const BACKEND_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET() {
  try {
    // Check if backend URL is configured
    const isConfigured = BACKEND_URL !== 'http://localhost:8000'
    
    // Try to reach the backend
    let backendHealthy = false
    let backendError: string | null = null
    
    if (isConfigured) {
      try {
        // Health endpoint doesn't have /api prefix
        const healthUrl = `${BACKEND_URL}/health`
        const response = await fetch(healthUrl, {
          method: 'GET',
          cache: 'no-store',
          signal: AbortSignal.timeout(5000), // 5 second timeout for health check
        })
        
        if (response.ok) {
          backendHealthy = true
        } else {
          backendError = `Backend returned status ${response.status}`
        }
      } catch (error) {
        if (error instanceof Error) {
          if (error.name === 'AbortError' || error.message.includes('timeout')) {
            backendError = 'Backend request timed out (5s). The pod may be starting up or overloaded.'
          } else if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch failed')) {
            backendError = `Cannot connect to backend. Pod may be stopped. Check RunPod console.`
          } else {
            backendError = error.message
          }
        } else {
          backendError = 'Unknown error'
        }
      }
    }
    
    return NextResponse.json({
      status: backendHealthy ? 'healthy' : 'unhealthy',
      configured: isConfigured,
      backendUrl: isConfigured ? BACKEND_URL : 'Not configured (using localhost fallback)',
      backendReachable: backendHealthy,
      error: backendError,
      message: isConfigured 
        ? (backendHealthy 
          ? 'Backend is configured and reachable' 
          : `Backend is configured but not reachable: ${backendError}`)
        : 'Backend URL not configured. Set API_URL or NEXT_PUBLIC_API_URL in Vercel environment variables.',
      hint: 'Set API_URL to your RunPod pod URL (e.g., https://9doems3qzzhna3-8888.proxy.runpod.net)'
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        configured: BACKEND_URL !== 'http://localhost:8000',
        backendUrl: BACKEND_URL
      },
      { status: 500 }
    )
  }
}

