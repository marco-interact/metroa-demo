import { NextRequest, NextResponse } from 'next/server'

// Backend URL - use environment variable or fallback to RunPod proxy
const BACKEND_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const path = searchParams.get('path') || ''
    
    // Proxy request to backend
    const backendUrl = `${BACKEND_URL}${path ? `/${path}` : ''}`
    
    const response = await fetch(backendUrl, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      console.error(`Backend error: ${response.status} ${response.statusText}`)
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to proxy request to backend:', error)
    return NextResponse.json(
      { error: 'Network error connecting to backend' },
      { status: 502 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const path = searchParams.get('path') || ''
    
    const body = await request.text()
    
    // Proxy request to backend
    const backendUrl = `${BACKEND_URL}${path ? `/${path}` : ''}`
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': request.headers.get('content-type') || 'application/json',
      },
      body: body,
    })

    if (!response.ok) {
      console.error(`Backend error: ${response.status} ${response.statusText}`)
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to proxy request to backend:', error)
    return NextResponse.json(
      { error: 'Network error connecting to backend' },
      { status: 502 }
    )
  }
}

