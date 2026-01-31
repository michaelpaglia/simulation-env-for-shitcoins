/**
 * Solana program constants for HOPIUM staking.
 */

// Program and token addresses from environment
export const HOPIUM_PROGRAM_ID =
  process.env.NEXT_PUBLIC_HOPIUM_PROGRAM_ID ||
  'Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS'

export const HOPIUM_MINT_ADDRESS =
  process.env.NEXT_PUBLIC_HOPIUM_MINT_ADDRESS ||
  'HopiumMint11111111111111111111111111111111111'

// Stake tiers (amounts in base units, assuming 6 decimals)
export const STAKE_TIERS = {
  0: { amount: 100_000_000, lockDays: 7, simHours: 12, label: 'Quick (12h)' },
  1: { amount: 500_000_000, lockDays: 3, simHours: 24, label: 'Standard (24h)' },
  2: { amount: 1_000_000_000, lockDays: 1, simHours: 48, label: 'Full (48h)' },
} as const

export type StakeTier = keyof typeof STAKE_TIERS

// Token decimals
export const TOKEN_DECIMALS = 6

// Burn rate (5%)
export const BURN_RATE_BPS = 500

// Emergency penalty (30%)
export const EMERGENCY_PENALTY_BPS = 3000

// PDA seeds (must match Anchor program)
export const STAKE_SEED = 'stake'
export const ESCROW_SEED = 'escrow'

/**
 * Convert token base units to display amount.
 */
export function toDisplayAmount(baseUnits: number): number {
  return baseUnits / Math.pow(10, TOKEN_DECIMALS)
}

/**
 * Convert display amount to base units.
 */
export function toBaseUnits(displayAmount: number): number {
  return Math.floor(displayAmount * Math.pow(10, TOKEN_DECIMALS))
}
