'use client'

import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'hopium_wallet'
const INITIAL_BALANCE = 1000
const BURN_RATE = 0.05 // 5% burn on each simulation

export interface WalletState {
  balance: number
  totalStaked: number
  totalBurned: number
  simulationsRun: number
}

const DEFAULT_STATE: WalletState = {
  balance: INITIAL_BALANCE,
  totalStaked: 0,
  totalBurned: 0,
  simulationsRun: 0,
}

export function useWallet() {
  const [wallet, setWallet] = useState<WalletState>(DEFAULT_STATE)
  const [pendingStake, setPendingStake] = useState<number | null>(null)

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setWallet(JSON.parse(saved))
      } catch {
        // Invalid data, use defaults
      }
    }
  }, [])

  // Save to localStorage on change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(wallet))
  }, [wallet])

  // Stake tokens before simulation
  const stake = useCallback((amount: number): boolean => {
    if (amount > wallet.balance) return false

    setWallet(prev => ({
      ...prev,
      balance: prev.balance - amount,
    }))
    setPendingStake(amount)
    return true
  }, [wallet.balance])

  // Complete simulation - return stake minus burn
  const completeSimulation = useCallback(() => {
    if (pendingStake === null) return

    const burnAmount = Math.floor(pendingStake * BURN_RATE)
    const returnAmount = pendingStake - burnAmount

    setWallet(prev => ({
      ...prev,
      balance: prev.balance + returnAmount,
      totalStaked: prev.totalStaked + pendingStake,
      totalBurned: prev.totalBurned + burnAmount,
      simulationsRun: prev.simulationsRun + 1,
    }))
    setPendingStake(null)
  }, [pendingStake])

  // Refund stake if simulation fails
  const refundStake = useCallback(() => {
    if (pendingStake === null) return

    setWallet(prev => ({
      ...prev,
      balance: prev.balance + pendingStake,
    }))
    setPendingStake(null)
  }, [pendingStake])

  // Check if user can afford stake
  const canAfford = useCallback((amount: number): boolean => {
    return wallet.balance >= amount
  }, [wallet.balance])

  // Reset wallet (for testing/faucet)
  const resetWallet = useCallback(() => {
    setWallet(DEFAULT_STATE)
    setPendingStake(null)
  }, [])

  // Claim faucet tokens (when broke)
  const claimFaucet = useCallback(() => {
    if (wallet.balance <= 0) {
      setWallet(prev => ({
        ...prev,
        balance: INITIAL_BALANCE,
      }))
    }
  }, [wallet.balance])

  return {
    ...wallet,
    pendingStake,
    stake,
    completeSimulation,
    refundStake,
    canAfford,
    resetWallet,
    claimFaucet,
    BURN_RATE,
  }
}

// Stake tiers - determines simulation depth and lock period
// Higher stake = deeper sim + shorter lock (rewards commitment)
export const STAKE_TIERS = {
  100: { hours: 12, lockDays: 7, label: 'Quick (12h)', lockLabel: '7 day lock' },
  500: { hours: 24, lockDays: 3, label: 'Standard (24h)', lockLabel: '3 day lock' },
  1000: { hours: 48, lockDays: 1, label: 'Full (48h)', lockLabel: '1 day lock' },
} as const

export type StakeTier = keyof typeof STAKE_TIERS
