'use client'

import { motion } from 'framer-motion'
import { MainLayout } from '@/components/layout/main-layout'
import { Loading } from '@/components/ui/loading'

export default function LoadingPage() {
  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center text-center"
      >
        <Loading size="lg" className="mx-auto" />
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-4 text-lg text-muted-foreground"
        >
          Loading...
        </motion.p>
      </motion.div>
    </MainLayout>
  )
} 