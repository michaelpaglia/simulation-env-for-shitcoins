'use client'

import { ReactNode } from 'react'
import { WalletProviders } from './WalletProviders'

interface ClientProvidersProps {
  children: ReactNode
}

export function ClientProviders({ children }: ClientProvidersProps) {
  return (
    <WalletProviders>
      {children}
    </WalletProviders>
  )
}
