'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { useCallback } from 'react'

export function useAuth() {
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

  const truncatedAddress = publicKey
    ? `${publicKey.toBase58().slice(0, 4)}...${publicKey.toBase58().slice(-4)}`
    : null

  return {
    isConnected: connected,
    isConnecting: connecting,
    publicKey: publicKey?.toBase58() ?? null,
    truncatedAddress,
    connect,
    disconnect,
  }
}
