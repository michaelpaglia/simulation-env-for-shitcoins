'use client'

import { useState, useEffect, useCallback } from 'react'
import { useConnection, useWallet } from '@solana/wallet-adapter-react'
import { PublicKey } from '@solana/web3.js'
import { getAccount, getAssociatedTokenAddress } from '@solana/spl-token'
import {
  HOPIUM_MINT_ADDRESS,
  TOKEN_DECIMALS,
  toDisplayAmount,
} from '@/lib/solana/constants'

export interface TokenBalance {
  /** Balance in base units (with decimals) */
  raw: number
  /** Balance as display number (e.g., 1000.50) */
  display: number
  /** Formatted string (e.g., "1,000.50") */
  formatted: string
}

export interface UseSolanaTokenReturn {
  balance: TokenBalance | null
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
}

/**
 * Hook to fetch real SPL token balance from Solana.
 */
export function useSolanaToken(): UseSolanaTokenReturn {
  const { connection } = useConnection()
  const { publicKey, connected } = useWallet()

  const [balance, setBalance] = useState<TokenBalance | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchBalance = useCallback(async () => {
    if (!publicKey || !connected) {
      setBalance(null)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const mint = new PublicKey(HOPIUM_MINT_ADDRESS)
      const ata = await getAssociatedTokenAddress(mint, publicKey)

      try {
        const account = await getAccount(connection, ata)
        const raw = Number(account.amount)
        const display = toDisplayAmount(raw)
        const formatted = display.toLocaleString('en-US', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
        })

        setBalance({ raw, display, formatted })
      } catch {
        // Token account doesn't exist = 0 balance
        setBalance({ raw: 0, display: 0, formatted: '0' })
      }
    } catch (err) {
      console.error('Failed to fetch token balance:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch balance')
      setBalance(null)
    } finally {
      setIsLoading(false)
    }
  }, [connection, publicKey, connected])

  // Fetch on mount and when wallet changes
  useEffect(() => {
    fetchBalance()
  }, [fetchBalance])

  // Poll for balance updates every 30 seconds
  useEffect(() => {
    if (!connected) return

    const interval = setInterval(fetchBalance, 30000)
    return () => clearInterval(interval)
  }, [connected, fetchBalance])

  return {
    balance,
    isLoading,
    error,
    refetch: fetchBalance,
  }
}
