'use client'

import { useState, useEffect, useCallback } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { config } from '@/config'

export interface StakeInfo {
  pda: string
  tier: number
  amount: number
  staked_at: string
  unlock_at: string
  simulation_used: boolean
  simulation_id: string | null
  burned: boolean
  can_release: boolean
  is_locked: boolean
  sim_hours: number
}

export interface WalletStakeStatus {
  wallet: string
  token_balance: number
  token_balance_display: string
  stakes: StakeInfo[]
  available_tiers: number[]
}

export interface UseStakeStatusReturn {
  status: WalletStakeStatus | null
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
  hasActiveStake: (tier: number) => boolean
  getStakeForTier: (tier: number) => StakeInfo | undefined
}

/**
 * Hook to fetch stake status from the backend API.
 */
export function useStakeStatus(): UseStakeStatusReturn {
  const { publicKey, connected } = useWallet()

  const [status, setStatus] = useState<WalletStakeStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = useCallback(async () => {
    if (!publicKey || !connected) {
      setStatus(null)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${config.apiUrl}/stake/status/${publicKey.toBase58()}`
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch stake status: ${response.statusText}`)
      }

      const data: WalletStakeStatus = await response.json()
      setStatus(data)
    } catch (err) {
      console.error('Failed to fetch stake status:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch stake status')
      setStatus(null)
    } finally {
      setIsLoading(false)
    }
  }, [publicKey, connected])

  // Fetch on mount and when wallet changes
  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const hasActiveStake = useCallback(
    (tier: number): boolean => {
      if (!status) return false
      return status.stakes.some(
        s => s.tier === tier && !s.can_release
      )
    },
    [status]
  )

  const getStakeForTier = useCallback(
    (tier: number): StakeInfo | undefined => {
      if (!status) return undefined
      return status.stakes.find(s => s.tier === tier)
    },
    [status]
  )

  return {
    status,
    isLoading,
    error,
    refetch: fetchStatus,
    hasActiveStake,
    getStakeForTier,
  }
}

/**
 * Verify a stake with the backend before simulation.
 */
export async function verifyStake(
  wallet: string,
  stakePda: string,
  tier?: number
): Promise<{ valid: boolean; error?: string; sim_hours?: number }> {
  try {
    const response = await fetch(`${config.apiUrl}/stake/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallet, stake_pda: stakePda, tier }),
    })

    const data = await response.json()

    if (!response.ok || !data.valid) {
      return {
        valid: false,
        error: data.message || 'Invalid stake',
      }
    }

    return {
      valid: true,
      sim_hours: data.sim_hours,
    }
  } catch (err) {
    return {
      valid: false,
      error: err instanceof Error ? err.message : 'Verification failed',
    }
  }
}
