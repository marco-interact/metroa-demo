"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  Square, 
  RotateCcw, 
  CheckCircle, 
  XCircle, 
  Clock,
  Zap
} from "lucide-react"

interface ProcessingStatusProps {
  scanId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  currentStage?: string
  onCancel?: () => void
  onRetry?: () => void
  className?: string
}

// Define all processing stages with their progress ranges
const PROCESSING_STAGES = [
  { name: 'Extracting frames from video...', min: 0, max: 15, icon: '📹' },
  { name: 'Extracting SIFT features...', min: 15, max: 35, icon: '🔍' },
  { name: 'Matching features between images...', min: 35, max: 55, icon: '🔗' },
  { name: 'Running sparse reconstruction...', min: 55, max: 70, icon: '🏗️' },
  { name: 'Running dense reconstruction...', min: 70, max: 95, icon: '🔬' },
  { name: 'Finalizing reconstruction...', min: 95, max: 100, icon: '✅' },
]

export function ProcessingStatus({
  scanId,
  status,
  progress,
  message,
  currentStage,
  onCancel,
  onRetry,
  className = ""
}: ProcessingStatusProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)

  // Calculate elapsed time
  useEffect(() => {
    if (status === 'processing') {
      const interval = setInterval(() => {
        setElapsedTime(prev => prev + 1)
      }, 1000)
      return () => clearInterval(interval)
    } else {
      setElapsedTime(0)
    }
  }, [status])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'processing':
        return <Zap className="w-4 h-4 text-blue-500 animate-pulse" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'border-yellow-500/20 bg-yellow-500/5'
      case 'processing':
        return 'border-blue-500/20 bg-blue-500/5'
      case 'completed':
        return 'border-green-500/20 bg-green-500/5'
      case 'failed':
        return 'border-red-500/20 bg-red-500/5'
      default:
        return 'border-gray-500/20 bg-gray-500/5'
    }
  }

  const getProgressColor = () => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500'
      case 'processing':
        return 'bg-blue-500'
      case 'completed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <Card className={`p-4 ${getStatusColor()} ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="font-medium text-sm">
            {status === 'pending' && 'Waiting to start'}
            {status === 'processing' && 'Processing...'}
            {status === 'completed' && 'Completed'}
            {status === 'failed' && 'Failed'}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {status === 'processing' && (
            <span className="text-xs text-gray-500">
              {formatTime(elapsedTime)}
            </span>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs"
          >
            {isExpanded ? 'Hide' : 'Details'}
          </Button>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
          <span>Overall Progress</span>
          <span className="font-semibold text-white">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        </div>
      </div>

      {/* Current Stage Message */}
      <div className="text-sm text-white mb-4 font-medium">
        {currentStage || message || 'Processing...'}
      </div>

      {/* Stage-by-Stage Progress */}
      {status === 'processing' && (
        <div className="space-y-2 mb-3">
          <div className="text-xs text-gray-400 mb-2 font-medium">Processing Stages:</div>
          {PROCESSING_STAGES.map((stage, index) => {
            const isActive = currentStage?.includes(stage.name.split('...')[0]) || 
                           (progress >= stage.min && progress < stage.max)
            const isCompleted = progress >= stage.max
            const stageProgress = isCompleted ? 100 : 
                                 isActive ? ((progress - stage.min) / (stage.max - stage.min)) * 100 : 0
            
            return (
              <div key={index}>
                <div className="flex items-center justify-between text-xs py-1">
                  <div className="flex items-center space-x-2">
                    <span className={isCompleted ? 'text-green-400' : isActive ? 'text-blue-400' : 'text-gray-500'}>
                      {isCompleted ? '✓' : isActive ? '⟳' : '○'}
                    </span>
                    <span className={isCompleted ? 'text-green-300' : isActive ? 'text-white' : 'text-gray-500'}>
                      {stage.name}
                    </span>
                  </div>
                  <span className={`text-xs font-medium ${
                    isCompleted ? 'text-green-400' : isActive ? 'text-blue-400' : 'text-gray-500'
                  }`}>
                    {isCompleted ? '100%' : isActive ? `${Math.round(stageProgress)}%` : '—'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Expanded Details */}
      {isExpanded && (
        <div className="space-y-3 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-gray-500">Scan ID:</span>
              <span className="ml-2 font-mono">{scanId}</span>
            </div>
            <div>
              <span className="text-gray-500">Status:</span>
              <span className="ml-2 capitalize">{status}</span>
            </div>
            {status === 'processing' && (
              <>
                <div>
                  <span className="text-gray-500">Elapsed:</span>
                  <span className="ml-2">{formatTime(elapsedTime)}</span>
                </div>
                <div>
                  <span className="text-gray-500">Progress:</span>
                  <span className="ml-2">{Math.round(progress)}%</span>
                </div>
              </>
            )}
          </div>

          {/* Error Console for Failed Status */}
          {status === 'failed' && message && (
            <div className="mt-3">
              <div className="text-xs font-medium text-red-600 mb-2">Error Details:</div>
              <div className="bg-red-950/50 border border-red-500/30 rounded-lg p-3 font-mono text-xs text-red-200 max-h-48 overflow-y-auto">
                <pre className="whitespace-pre-wrap break-words">{message}</pre>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            {status === 'processing' && onCancel && (
              <Button
                variant="outline"
                size="sm"
                onClick={onCancel}
                className="text-xs"
              >
                <Square className="w-3 h-3 mr-1" />
                Cancel
              </Button>
            )}
            
            {status === 'failed' && onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="text-xs"
              >
                <RotateCcw className="w-3 h-3 mr-1" />
                Retry
              </Button>
            )}
            
            {status === 'completed' && (
              <Button
                variant="outline"
                size="sm"
                className="text-xs"
              >
                <CheckCircle className="w-3 h-3 mr-1" />
                View Results
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  )
}