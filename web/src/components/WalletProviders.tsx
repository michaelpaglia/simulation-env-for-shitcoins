'use client'

import { useMemo, ReactNode } from 'react'
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets'
import { clusterApiUrl, type Cluster } from '@solana/web3.js'

import '@solana/wallet-adapter-react-ui/styles.css'

interface WalletProvidersProps {
  children: ReactNode
}

const SUPPORTED_NETWORKS: Cluster[] = ['devnet', 'mainnet-beta', 'testnet']

function getNetwork(): Cluster {
  const env = process.env.NEXT_PUBLIC_SOLANA_NETWORK
  if (env && SUPPORTED_NETWORKS.includes(env as Cluster)) {
    return env as Cluster
  }
  return 'devnet'
}

/**
 * Provides Solana wallet context to the application.
 * Configure via environment variables:
 * - NEXT_PUBLIC_SOLANA_NETWORK: 'devnet' | 'mainnet-beta' | 'testnet'
 * - NEXT_PUBLIC_SOLANA_RPC_URL: Custom RPC endpoint (optional)
 */
export function WalletProviders({ children }: WalletProvidersProps) {
  const network = getNetwork()

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
