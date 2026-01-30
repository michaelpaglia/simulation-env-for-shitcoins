'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { useCallback, useMemo } from 'react'

export interface AuthState {
  isConnected: boolean
  isConnecting: boolean
  publicKey: string | null
  truncatedAddress: string | null
  connect: () => void
  disconnect: () => Promise<void>
}

/**
 * Hook for Solana wallet authentication state.
 * Wraps @solana/wallet-adapter-react for a simpler API.
 */
export function useAuth(): AuthState {
  const {
    publicKey,
    connected,
    connecting,
    disconnect: walletDisconnect,
    select,
    wallets,
  } = useWallet()

  const connect = useCallback(() => {
    const phantomWallet = wallets.find(w => w.adapter.name === 'Phantom')
    if (phantomWallet) {
      select(phantomWallet.adapter.name)
    }
  }, [wallets, select])

  const disconnect = useCallback(async () => {
    await walletDisconnect()
  }, [walletDisconnect])

  const publicKeyString = useMemo(() => {
    return publicKey?.toBase58() ?? null
  }, [publicKey])

  const truncatedAddress = useMemo(() => {
    if (!publicKeyString) return null
    return `${publicKeyString.slice(0, 4)}...${publicKeyString.slice(-4)}`
  }, [publicKeyString])

  return {
    isConnected: connected,
    isConnecting: connecting,
    publicKey: publicKeyString,
    truncatedAddress,
    connect,
    disconnect,
  }
}
