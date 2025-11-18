"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, FolderOpen, Plus, User, Menu } from "lucide-react"
import { cn } from "@/lib/utils"

interface MobileBottomNavProps {
  className?: string
}

export function MobileBottomNav({ className }: MobileBottomNavProps) {
  const pathname = usePathname()

  const navItems = [
    {
      label: "Home",
      href: "/",
      icon: Home,
      active: pathname === "/",
    },
    {
      label: "Projects",
      href: "/projects",
      icon: FolderOpen,
      active: pathname.startsWith("/projects"),
    },
    {
      label: "New",
      href: "/projects/new",
      icon: Plus,
      active: false,
      highlight: true,
    },
    {
      label: "Account",
      href: "/account",
      icon: User,
      active: pathname.startsWith("/account"),
    },
    {
      label: "Menu",
      href: "/menu",
      icon: Menu,
      active: pathname.startsWith("/menu"),
    },
  ]

  return (
    <nav className={cn(
      "fixed bottom-0 left-0 right-0 z-50 bg-surface-elevated border-t border-app-primary",
      "md:hidden", // Hide on desktop
      "safe-area-inset-bottom", // iOS safe area
      className
    )}>
      <div className="flex items-center justify-around h-16 px-2">
        {navItems.map((item) => {
          const Icon = item.icon
          
          if (item.highlight) {
            // Special styling for "New" button
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex flex-col items-center justify-center min-w-[64px] -mt-6"
              >
                <div className="w-14 h-14 rounded-full bg-primary-400 shadow-lg flex items-center justify-center hover:bg-primary-500 transition-all active:scale-95">
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </Link>
            )
          }

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center gap-1 min-w-[64px] py-2 px-3 rounded-lg transition-all active:scale-95",
                item.active
                  ? "text-primary-400"
                  : "text-gray-400 hover:text-white"
              )}
            >
              <Icon className={cn(
                "w-5 h-5",
                item.active && "drop-shadow-[0_0_8px_rgba(62,147,201,0.5)]"
              )} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

