'use client'

import { useState, useCallback } from 'react'
import { useConnection, useWallet } from '@solana/wallet-adapter-react'
import { PublicKey, Transaction } from '@solana/web3.js'
import {
  STAKE_TIERS,
  StakeTier,
  toDisplayAmount,
  BURN_RATE_BPS,
} from '@/lib/solana/constants'
import { getStakePdaAddress } from '@/lib/solana/pda'
import { buildStakeTransaction, buildEmergencyWithdrawTransaction, buildReleaseTransaction } from '@/lib/solana/instructions'
import { config } from '@/config'

export type StakingStatus = 'idle' | 'building' | 'signing' | 'confirming' | 'success' | 'error'

export interface StakingState {
  status: StakingStatus
  signature: string | null
  error: string | null
  tier: StakeTier | null
}

export interface UseStakingReturn {
  state: StakingState
  stake: (tier: StakeTier, escrowTokenAccount: string) => Promise<string | null>
  emergencyWithdraw: (tier: number, escrowTokenAccount: string) => Promise<string | null>
  release: (tier: number, escrowTokenAccount: string) => Promise<string | null>
  reset: () => void
  getStakePda: (tier: StakeTier) => string | null
}

/**
 * Hook for staking HOPIUM tokens on-chain.
 */
export function useStaking(): UseStakingReturn {
  const { connection } = useConnection()
  const { publicKey, signTransaction, connected } = useWallet()

  const [state, setState] = useState<StakingState>({
    status: 'idle',
    signature: null,
    error: null,
    tier: null,
  })

  const reset = useCallback(() => {
    setState({
      status: 'idle',
      signature: null,
      error: null,
      tier: null,
    })
  }, [])

  const getStakePda = useCallback(
    (tier: StakeTier): string | null => {
      if (!publicKey) return null
      return getStakePdaAddress(publicKey, tier)
    },
    [publicKey]
  )

  const stake = useCallback(
    async (tier: StakeTier, escrowTokenAccount: string): Promise<string | null> => {
      if (!publicKey || !signTransaction || !connected) {
        setState(prev => ({ ...prev, status: 'error', error: 'Wallet not connected' }))
        return null
      }

      setState({ status: 'building', signature: null, error: null, tier })

      try {
        // Build transaction
        const escrowPk = new PublicKey(escrowTokenAccount)
        const transaction = await buildStakeTransaction(
          connection,
          publicKey,
          tier,
          escrowPk
        )

        setState(prev => ({ ...prev, status: 'signing' }))

        // Sign transaction
        const signed = await signTransaction(transaction)

        setState(prev => ({ ...prev, status: 'confirming' }))

        // Send and confirm
        const signature = await connection.sendRawTransaction(signed.serialize())
        await connection.confirmTransaction(signature, 'confirmed')

        setState({
          status: 'success',
          signature,
          error: null,
          tier,
        })

        return signature
      } catch (err) {
        console.error('Staking failed:', err)
        setState({
          status: 'error',
          signature: null,
          error: err instanceof Error ? err.message : 'Staking failed',
          tier,
        })
        return null
      }
    },
    [connection, publicKey, signTransaction, connected]
  )

  const emergencyWithdraw = useCallback(
    async (tier: number, escrowTokenAccount: string): Promise<string | null> => {
      if (!publicKey || !signTransaction || !connected) {
        setState(prev => ({ ...prev, status: 'error', error: 'Wallet not connected' }))
        return null
      }

      setState({ status: 'building', signature: null, error: null, tier: tier as StakeTier })

      try {
        const escrowPk = new PublicKey(escrowTokenAccount)
        const transaction = await buildEmergencyWithdrawTransaction(
          connection,
          publicKey,
          tier,
          escrowPk
        )

        setState(prev => ({ ...prev, status: 'signing' }))
        const signed = await signTransaction(transaction)

        setState(prev => ({ ...prev, status: 'confirming' }))
        const signature = await connection.sendRawTransaction(signed.serialize())
        await connection.confirmTransaction(signature, 'confirmed')

        setState({
          status: 'success',
          signature,
          error: null,
          tier: tier as StakeTier,
        })

        return signature
      } catch (err) {
        console.error('Emergency withdraw failed:', err)
        setState({
          status: 'error',
          signature: null,
          error: err instanceof Error ? err.message : 'Emergency withdraw failed',
          tier: tier as StakeTier,
        })
        return null
      }
    },
    [connection, publicKey, signTransaction, connected]
  )

  const release = useCallback(
    async (tier: number, escrowTokenAccount: string): Promise<string | null> => {
      if (!publicKey || !signTransaction || !connected) {
        setState(prev => ({ ...prev, status: 'error', error: 'Wallet not connected' }))
        return null
      }

      setState({ status: 'building', signature: null, error: null, tier: tier as StakeTier })

      try {
        const escrowPk = new PublicKey(escrowTokenAccount)
        const transaction = await buildReleaseTransaction(
          connection,
          publicKey,
          tier,
          escrowPk
        )

        setState(prev => ({ ...prev, status: 'signing' }))
        const signed = await signTransaction(transaction)

        setState(prev => ({ ...prev, status: 'confirming' }))
        const signature = await connection.sendRawTransaction(signed.serialize())
        await connection.confirmTransaction(signature, 'confirmed')

        setState({
          status: 'success',
          signature,
          error: null,
          tier: tier as StakeTier,
        })

        return signature
      } catch (err) {
        console.error('Release failed:', err)
        setState({
          status: 'error',
          signature: null,
          error: err instanceof Error ? err.message : 'Release failed',
          tier: tier as StakeTier,
        })
        return null
      }
    },
    [connection, publicKey, signTransaction, connected]
  )

  return {
    state,
    stake,
    emergencyWithdraw,
    release,
    reset,
    getStakePda,
  }
}
