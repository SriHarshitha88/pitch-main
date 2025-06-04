import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LoadingProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function Loading({ className, size = 'md' }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <motion.div
        className={cn(
          'relative rounded-full border-2 border-primary/20',
          sizeClasses[size]
        )}
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
      >
        <motion.div
          className="absolute inset-0 rounded-full border-t-2 border-primary"
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </motion.div>
    </div>
  )
}

export function LoadingPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loading size="lg" className="mx-auto" />
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-4 text-lg text-muted-foreground"
        >
          Loading...
        </motion.p>
      </div>
    </div>
  )
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <motion.div
        className="relative h-8 w-8"
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
      >
        <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
        <div className="absolute inset-0 rounded-full border-t-2 border-primary" />
      </motion.div>
    </div>
  )
}

export function LoadingDots() {
  return (
    <div className="flex items-center justify-center space-x-2">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className="h-2 w-2 rounded-full bg-primary"
          animate={{
            y: [0, -10, 0],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: index * 0.2,
          }}
        />
      ))}
    </div>
  )
}

export function LoadingBar() {
  return (
    <div className="h-1 w-full overflow-hidden bg-primary/20">
      <motion.div
        className="h-full w-full bg-primary"
        initial={{ x: '-100%' }}
        animate={{ x: '100%' }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  )
} 