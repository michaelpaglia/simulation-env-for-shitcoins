'use client'

import { useMemo, ReactNode } from 'react'
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets'
import { clusterApiUrl } from '@solana/web3.js'

import '@solana/wallet-adapter-react-ui/styles.css'

interface WalletProvidersProps {
  children: ReactNode
}

export function WalletProviders({ children }: WalletProvidersProps) {
  const network = process.env.NEXT_PUBLIC_SOLANA_NETWORK === 'mainnet-beta'
    ? 'mainnet-beta'
    : 'devnet'

  const endpoint = useMemo(() => {
    return process.env.NEXT_PUBLIC_SOLANA_RPC_URL || clusterApiUrl(network)
  }, [network])

  const wallets = useMemo(() => [
    new PhantomWalletAdapter(),
  ], [])

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          {children}
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  )
}
