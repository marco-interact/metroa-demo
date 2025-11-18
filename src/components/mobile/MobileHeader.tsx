"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, X, ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface MobileHeaderProps {
  title: string
  showBack?: boolean
  onBack?: () => void
  className?: string
}

export function MobileHeader({ title, showBack, onBack, className }: MobileHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <>
      {/* Header Bar */}
      <header className={cn(
        "fixed top-0 left-0 right-0 z-40 bg-surface-elevated/95 backdrop-blur-md border-b border-app-primary",
        "md:hidden", // Hide on desktop
        "safe-area-inset-top", // iOS safe area
        className
      )}>
        <div className="flex items-center justify-between h-14 px-4">
          {/* Left: Back or Menu */}
          {showBack ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBack}
              className="p-2 -ml-2"
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 -ml-2"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          )}

          {/* Center: Title */}
          <h1 className="text-base font-semibold text-white truncate flex-1 mx-4 text-center">
            {title}
          </h1>

          {/* Right: Placeholder for actions */}
          <div className="w-10" />
        </div>
      </header>

      {/* Slide-out Menu */}
      {menuOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 bg-black/50 z-30 md:hidden"
            onClick={() => setMenuOpen(false)}
          />

          {/* Menu Drawer */}
          <div className={cn(
            "fixed top-14 left-0 bottom-0 w-64 bg-surface-elevated border-r border-app-primary z-30 md:hidden",
            "animate-slide-in-left"
          )}>
            <nav className="flex flex-col p-4 space-y-2">
              <Link
                href="/"
                className="px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-surface-tertiary rounded-lg transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Home
              </Link>
              <Link
                href="/projects"
                className="px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-surface-tertiary rounded-lg transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Projects
              </Link>
              <Link
                href="/projects/new"
                className="px-4 py-3 text-sm text-primary-400 font-medium hover:bg-surface-tertiary rounded-lg transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                New Project
              </Link>
              
              <div className="border-t border-app-secondary my-2" />
              
              <Link
                href="/settings"
                className="px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-surface-tertiary rounded-lg transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Settings
              </Link>
              <Link
                href="/help"
                className="px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-surface-tertiary rounded-lg transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Help & Support
              </Link>
            </nav>
          </div>
        </>
      )}

      {/* Spacer to prevent content from going under header */}
      <div className="h-14 md:hidden" />
    </>
  )
}

