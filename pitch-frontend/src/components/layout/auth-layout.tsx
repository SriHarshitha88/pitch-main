import React from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/ui/theme-toggle'

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      {/* Premium Header */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
        className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      >
        <div className="container flex h-16 items-center justify-between">
          <Button variant="ghost" className="text-xl font-bold">
            Pitch
          </Button>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="container flex min-h-[calc(100vh-4rem)] items-center justify-center py-8"
      >
        <div className="relative w-full max-w-md">
          <div className="absolute inset-0 -z-10 gradient-mesh" />
          <div className="glass-effect rounded-lg p-8">
            {children}
          </div>
        </div>
      </motion.main>

      {/* Premium Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="border-t bg-background"
      >
        <div className="container py-4 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Pitch. All rights reserved.
        </div>
      </motion.footer>
    </div>
  )
} 