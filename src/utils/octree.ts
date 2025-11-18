/**
 * Octree Spatial Partitioning for Efficient Point Cloud Operations
 * 
 * Used for:
 * - Fast collision detection
 * - Efficient point cloud rendering (LOD)
 * - Spatial queries
 */

import * as THREE from 'three'

interface OctreeNode {
  bounds: THREE.Box3
  points: THREE.Vector3[]
  children: OctreeNode[] | null
  center: THREE.Vector3
  size: number
}

export class Octree {
  private root: OctreeNode
  private maxPointsPerNode: number
  private maxDepth: number

  constructor(
    bounds: THREE.Box3,
    maxPointsPerNode: number = 100,
    maxDepth: number = 8
  ) {
    this.maxPointsPerNode = maxPointsPerNode
    this.maxDepth = maxDepth
    
    const center = new THREE.Vector3()
    bounds.getCenter(center)
    const size = bounds.getSize(new THREE.Vector3()).length()

    this.root = {
      bounds,
      points: [],
      children: null,
      center,
      size
    }
  }

  /**
   * Build octree from point cloud geometry
   */
  static fromGeometry(geometry: THREE.BufferGeometry): Octree {
    const positions = geometry.getAttribute('position')
    
    // Compute bounds
    geometry.computeBoundingBox()
    const bounds = geometry.boundingBox!.clone()
    
    // Expand bounds slightly to avoid edge cases
    bounds.expandByScalar(0.1)
    
    const octree = new Octree(bounds)
    
    // Insert all points
    for (let i = 0; i < positions.count; i++) {
      const point = new THREE.Vector3(
        positions.getX(i),
        positions.getY(i),
        positions.getZ(i)
      )
      octree.insert(point)
    }
    
    return octree
  }

  /**
   * Insert a point into the octree
   */
  insert(point: THREE.Vector3, node: OctreeNode = this.root, depth: number = 0): boolean {
    // Check if point is within bounds
    if (!node.bounds.containsPoint(point)) {
      return false
    }

    // If this is a leaf node with space, add the point
    if (node.children === null) {
      node.points.push(point)
      
      // Split if we exceeded capacity and haven't reached max depth
      if (node.points.length > this.maxPointsPerNode && depth < this.maxDepth) {
        this.split(node)
        
        // Redistribute points to children
        const pointsToRedistribute = [...node.points]
        node.points = []
        
        for (const p of pointsToRedistribute) {
          this.insertIntoChildren(p, node)
        }
      }
      
      return true
    }

    // Insert into appropriate child
    return this.insertIntoChildren(point, node)
  }

  private insertIntoChildren(point: THREE.Vector3, node: OctreeNode): boolean {
    if (!node.children) return false
    
    for (const child of node.children) {
      if (this.insert(point, child, 0)) {
        return true
      }
    }
    
    return false
  }

  /**
   * Split a node into 8 children
   */
  private split(node: OctreeNode): void {
    const { bounds } = node
    const center = new THREE.Vector3()
    bounds.getCenter(center)
    
    const min = bounds.min
    const max = bounds.max
    
    node.children = []
    
    // Create 8 octants
    for (let x = 0; x < 2; x++) {
      for (let y = 0; y < 2; y++) {
        for (let z = 0; z < 2; z++) {
          const childMin = new THREE.Vector3(
            x === 0 ? min.x : center.x,
            y === 0 ? min.y : center.y,
            z === 0 ? min.z : center.z
          )
          
          const childMax = new THREE.Vector3(
            x === 0 ? center.x : max.x,
            y === 0 ? center.y : max.y,
            z === 0 ? center.z : max.z
          )
          
          const childBounds = new THREE.Box3(childMin, childMax)
          const childCenter = new THREE.Vector3()
          childBounds.getCenter(childCenter)
          const childSize = childBounds.getSize(new THREE.Vector3()).length()
          
          node.children.push({
            bounds: childBounds,
            points: [],
            children: null,
            center: childCenter,
            size: childSize
          })
        }
      }
    }
  }

  /**
   * Find nearest point to a position (for collision detection)
   */
  findNearestPoint(position: THREE.Vector3, maxDistance: number = Infinity): THREE.Vector3 | null {
    let nearest: THREE.Vector3 | null = null
    let nearestDistance = maxDistance

    this.searchNearestPoint(this.root, position, (point, distance) => {
      if (distance < nearestDistance) {
        nearest = point
        nearestDistance = distance
      }
    })

    return nearest
  }

  private searchNearestPoint(
    node: OctreeNode,
    position: THREE.Vector3,
    callback: (point: THREE.Vector3, distance: number) => void
  ): void {
    // Check if we should search this node
    const closestPoint = new THREE.Vector3()
    node.bounds.clampPoint(position, closestPoint)
    const distanceToBounds = position.distanceTo(closestPoint)
    
    // If bounds are too far, skip this node
    if (distanceToBounds > 10) return // Early exit for far nodes
    
    // Check points in this node
    for (const point of node.points) {
      const distance = position.distanceTo(point)
      callback(point, distance)
    }
    
    // Search children if they exist
    if (node.children) {
      // Sort children by distance to position for better pruning
      const childrenWithDistance = node.children.map(child => ({
        node: child,
        distance: position.distanceTo(child.center)
      }))
      
      childrenWithDistance.sort((a, b) => a.distance - b.distance)
      
      for (const { node: child } of childrenWithDistance) {
        this.searchNearestPoint(child, position, callback)
      }
    }
  }

  /**
   * Find all points within a sphere (for local collision detection)
   */
  findPointsInSphere(center: THREE.Vector3, radius: number): THREE.Vector3[] {
    const result: THREE.Vector3[] = []
    this.searchInSphere(this.root, center, radius, result)
    return result
  }

  private searchInSphere(
    node: OctreeNode,
    center: THREE.Vector3,
    radius: number,
    result: THREE.Vector3[]
  ): void {
    // Check if sphere intersects node bounds
    const closestPoint = new THREE.Vector3()
    node.bounds.clampPoint(center, closestPoint)
    const distance = center.distanceTo(closestPoint)
    
    if (distance > radius) return
    
    // Check points in this node
    const radiusSquared = radius * radius
    for (const point of node.points) {
      if (center.distanceToSquared(point) <= radiusSquared) {
        result.push(point)
      }
    }
    
    // Search children
    if (node.children) {
      for (const child of node.children) {
        this.searchInSphere(child, center, radius, result)
      }
    }
  }

  /**
   * Get statistics about the octree
   */
  getStats(): { nodes: number; points: number; maxDepth: number } {
    let nodes = 0
    let points = 0
    let maxDepth = 0

    const traverse = (node: OctreeNode, depth: number) => {
      nodes++
      points += node.points.length
      maxDepth = Math.max(maxDepth, depth)
      
      if (node.children) {
        for (const child of node.children) {
          traverse(child, depth + 1)
        }
      }
    }

    traverse(this.root, 0)
    
    return { nodes, points, maxDepth }
  }
}

