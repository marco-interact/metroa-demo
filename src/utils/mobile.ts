/**
 * Mobile Device Detection and Utilities
 */

export function isMobileDevice(): boolean {
  // Server-side rendering safety
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return false
  }
  
  try {
    // Check user agent
    const userAgent = navigator.userAgent.toLowerCase()
    const mobileKeywords = ['android', 'webos', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
    const isMobileUA = mobileKeywords.some(keyword => userAgent.includes(keyword))
    
    // Check screen size
    const isSmallScreen = window.innerWidth < 768
    
    // Check touch support
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0
    
    return isMobileUA || (isSmallScreen && hasTouch)
  } catch {
    return false
  }
}

export function isTablet(): boolean {
  // Server-side rendering safety
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return false
  }
  
  try {
    const userAgent = navigator.userAgent.toLowerCase()
    const isIPad = userAgent.includes('ipad') || (userAgent.includes('macintosh') && navigator.maxTouchPoints > 1)
    const isAndroidTablet = userAgent.includes('android') && !userAgent.includes('mobile')
    
    const width = window.innerWidth
    const isTabletSize = width >= 768 && width < 1024
    
    return isIPad || isAndroidTablet || isTabletSize
  } catch {
    return false
  }
}

export function getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
  if (isMobileDevice() && !isTablet()) return 'mobile'
  if (isTablet()) return 'tablet'
  return 'desktop'
}

export function getOptimalPointCloudSize(totalPoints: number): number {
  const deviceType = getDeviceType()
  
  switch (deviceType) {
    case 'mobile':
      // Mobile: max 500K points for smooth performance and stability
      return Math.min(totalPoints, 500_000)
    case 'tablet':
      // Tablet: max 1.5M points
      return Math.min(totalPoints, 1_500_000)
    case 'desktop':
      // Desktop: max 3M points (reduced to prevent WebGL context loss)
      return Math.min(totalPoints, 3_000_000)
    default:
      return totalPoints
  }
}

export function getCanvasConfig(deviceType: 'mobile' | 'tablet' | 'desktop') {
  switch (deviceType) {
    case 'mobile':
      return {
        antialias: false,
        powerPreference: 'default' as const, // Battery-friendly
        pixelRatio: Math.min(window.devicePixelRatio, 2), // Cap pixel ratio
        shadowMap: false,
        preserveDrawingBuffer: false,
      }
    case 'tablet':
      return {
        antialias: false,
        powerPreference: 'high-performance' as const,
        pixelRatio: Math.min(window.devicePixelRatio, 2),
        shadowMap: false,
        preserveDrawingBuffer: false,
      }
    case 'desktop':
      return {
        antialias: false,
        powerPreference: 'high-performance' as const,
        pixelRatio: window.devicePixelRatio,
        shadowMap: false,
        preserveDrawingBuffer: false,
      }
  }
}

export function shouldEnableCollision(): boolean {
  // Disable collision on mobile for better performance
  const deviceType = getDeviceType()
  return deviceType !== 'mobile'
}

export function getPointSize(deviceType: 'mobile' | 'tablet' | 'desktop'): number {
  switch (deviceType) {
    case 'mobile':
      return 0.004 // Larger points on mobile for visibility
    case 'tablet':
      return 0.003
    case 'desktop':
      return 0.002
  }
}

export function supportsWebGL2(): boolean {
  if (typeof window === 'undefined') return false
  
  try {
    const canvas = document.createElement('canvas')
    return !!(window.WebGL2RenderingContext && canvas.getContext('webgl2'))
  } catch {
    return false
  }
}

export function getViewportSize() {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
    isMobile: window.innerWidth < 768,
    isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
    isDesktop: window.innerWidth >= 1024,
  }
}

