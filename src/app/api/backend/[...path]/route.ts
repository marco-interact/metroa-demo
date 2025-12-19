import { NextRequest, NextResponse } from 'next/server'

// Backend URL - use environment variable or fallback to RunPod proxy
// This should be set in Vercel environment variables to your RunPod pod URL
// Current pod: https://9doems3qzzhna3-8888.proxy.runpod.net
const BACKEND_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Log backend URL configuration (without exposing sensitive data)
if (process.env.NODE_ENV === 'production') {
  console.log('[API Proxy] Backend URL configured:', BACKEND_URL ? '✅ Set' : '❌ Missing - using localhost fallback')
}

// Helper to get the full backend URL for a given path
// Some endpoints like /health don't have /api prefix, others do
function getBackendUrl(pathSegments: string[]): string {
  if (pathSegments.length === 0) {
    return `${BACKEND_URL}`
  }
  
  const path = `/${pathSegments.join('/')}`
  
  // Endpoints that don't have /api prefix
  const noApiPrefix = ['health', 'demo-resources', 'results']
  const firstSegment = pathSegments[0]
  
  if (noApiPrefix.includes(firstSegment)) {
    return `${BACKEND_URL}${path}`
  }
  
  // All other endpoints have /api prefix
  return `${BACKEND_URL}/api${path}`
}

// Helper to forward headers (excluding host and connection)
function getForwardHeaders(request: NextRequest): HeadersInit {
  const headers: HeadersInit = {}
  
  // Forward important headers
  const contentType = request.headers.get('content-type')
  if (contentType) {
    headers['Content-Type'] = contentType
  }
  
  const authorization = request.headers.get('authorization')
  if (authorization) {
    headers['Authorization'] = authorization
  }
  
  return headers
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> | { path: string[] } }
) {
  try {
    // Handle both sync and async params (Next.js 13+ vs 15+)
    const resolvedParams = await Promise.resolve(params)
    const pathSegments = Array.isArray(resolvedParams.path) ? resolvedParams.path : [resolvedParams.path].filter(Boolean)
    
    const backendUrl = getBackendUrl(pathSegments)
    const searchParams = request.nextUrl.searchParams.toString()
    const fullUrl = searchParams ? `${backendUrl}?${searchParams}` : backendUrl
    
    console.log(`[API Proxy] GET ${fullUrl} (from path: ${pathSegments.join('/')})`)
    
    // Check if backend URL is configured
    if (BACKEND_URL === 'http://localhost:8000' && process.env.NODE_ENV === 'production') {
      console.error('[API Proxy] ❌ Backend URL not configured! Set API_URL or NEXT_PUBLIC_API_URL in Vercel environment variables')
      return NextResponse.json(
        { 
          error: 'Backend not configured',
          message: 'API_URL environment variable is not set. Please configure it in Vercel settings.',
          hint: 'Set API_URL to your RunPod pod URL (e.g., https://9doems3qzzhna3-8888.proxy.runpod.net)'
        },
        { status: 502 }
      )
    }
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: getForwardHeaders(request),
      cache: 'no-store',
      // Add timeout for production
      signal: AbortSignal.timeout(30000), // 30 second timeout
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[API Proxy] Backend error ${response.status}: ${errorText}`)
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: errorText },
        { status: response.status }
      )
    }

    // Handle different response types
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      const data = await response.json()
      return NextResponse.json(data)
    } else {
      const data = await response.text()
      return new NextResponse(data, {
        headers: {
          'Content-Type': contentType || 'text/plain',
        },
      })
    }
  } catch (error) {
    console.error('[API Proxy] Failed to proxy GET request:', error)
    
    // Provide more helpful error messages
    let errorMessage = 'Network error connecting to backend'
    if (error instanceof Error) {
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        errorMessage = 'Backend request timed out (30s). The backend may be slow or unavailable.'
      } else if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
        errorMessage = `Cannot connect to backend at ${BACKEND_URL}. Is the RunPod pod running?`
      } else {
        errorMessage = error.message
      }
    }
    
    return NextResponse.json(
      { 
        error: 'Network error connecting to backend',
        message: errorMessage,
        backendUrl: BACKEND_URL,
        configured: BACKEND_URL !== 'http://localhost:8000'
      },
      { status: 502 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> | { path: string[] } }
) {
  try {
    // Handle both sync and async params (Next.js 13+ vs 15+)
    const resolvedParams = await Promise.resolve(params)
    const pathSegments = Array.isArray(resolvedParams.path) ? resolvedParams.path : [resolvedParams.path].filter(Boolean)
    
    const backendUrl = getBackendUrl(pathSegments)
    
    console.log(`[API Proxy] POST ${backendUrl}`)
    
    // Get request body
    let body: string | FormData | undefined
    const contentType = request.headers.get('content-type')
    
    if (contentType?.includes('multipart/form-data')) {
      body = await request.formData()
    } else if (contentType?.includes('application/json')) {
      body = await request.text()
    } else {
      body = await request.text()
    }
    
    // Check if backend URL is configured
    if (BACKEND_URL === 'http://localhost:8000' && process.env.NODE_ENV === 'production') {
      console.error('[API Proxy] ❌ Backend URL not configured!')
      return NextResponse.json(
        { 
          error: 'Backend not configured',
          message: 'API_URL environment variable is not set. Please configure it in Vercel settings.'
        },
        { status: 502 }
      )
    }
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: getForwardHeaders(request),
      body: body as any,
      signal: AbortSignal.timeout(30000), // 30 second timeout
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[API Proxy] Backend error ${response.status}: ${errorText}`)
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: errorText },
        { status: response.status }
      )
    }

    const responseContentType = response.headers.get('content-type')
    if (responseContentType?.includes('application/json')) {
      const data = await response.json()
      return NextResponse.json(data)
    } else {
      const data = await response.text()
      return new NextResponse(data, {
        headers: {
          'Content-Type': responseContentType || 'text/plain',
        },
      })
    }
  } catch (error) {
    console.error('[API Proxy] Failed to proxy POST request:', error)
    return NextResponse.json(
      { 
        error: 'Network error connecting to backend',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 502 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> | { path: string[] } }
) {
  try {
    const resolvedParams = await Promise.resolve(params)
    const pathSegments = Array.isArray(resolvedParams.path) ? resolvedParams.path : [resolvedParams.path].filter(Boolean)
    const backendUrl = getBackendUrl(pathSegments)
    
    const body = await request.text()
    
    const response = await fetch(backendUrl, {
      method: 'PUT',
      headers: getForwardHeaders(request),
      body: body,
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to proxy PUT request:', error)
    return NextResponse.json(
      { error: 'Network error connecting to backend' },
      { status: 502 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> | { path: string[] } }
) {
  try {
    const resolvedParams = await Promise.resolve(params)
    const pathSegments = Array.isArray(resolvedParams.path) ? resolvedParams.path : [resolvedParams.path].filter(Boolean)
    const backendUrl = getBackendUrl(pathSegments)
    
    const response = await fetch(backendUrl, {
      method: 'DELETE',
      headers: getForwardHeaders(request),
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to proxy DELETE request:', error)
    return NextResponse.json(
      { error: 'Network error connecting to backend' },
      { status: 502 }
    )
  }
}

