import { motion } from 'framer-motion'
import { Button } from './button'
import { cn } from '@/lib/utils'

interface ErrorProps {
  title?: string
  message?: string
  className?: string
  onRetry?: () => void
}

export function Error({
  title = 'Something went wrong',
  message = 'An error occurred while processing your request.',
  className,
  onRetry,
}: ErrorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn('flex flex-col items-center justify-center p-8 text-center', className)}
    >
      <motion.div
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-6 rounded-full bg-destructive/10 p-4"
      >
        <svg
          className="h-12 w-12 text-destructive"
          fill="none"
          height="24"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          width="24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" x2="12" y1="8" y2="12" />
          <line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
      </motion.div>
      <motion.h2
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="mb-2 text-2xl font-bold"
      >
        {title}
      </motion.h2>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mb-6 text-muted-foreground"
      >
        {message}
      </motion.p>
      {onRetry && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Button onClick={onRetry} variant="outline">
            Try Again
          </Button>
        </motion.div>
      )}
    </motion.div>
  )
}

export function ErrorPage({
  title = 'Page Not Found',
  message = 'The page you are looking for does not exist.',
  className,
  onRetry,
}: ErrorProps) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Error
        title={title}
        message={message}
        className={className}
        onRetry={onRetry}
      />
    </div>
  )
}

export function ErrorBoundary({
  title = 'Something went wrong',
  message = 'An unexpected error occurred.',
  className,
  onRetry,
}: ErrorProps) {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <Error
        title={title}
        message={message}
        className={className}
        onRetry={onRetry}
      />
    </div>
  )
} 