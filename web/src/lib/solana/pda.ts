/**
 * PDA derivation utilities for HOPIUM staking.
 */

import { PublicKey } from '@solana/web3.js'
import { HOPIUM_PROGRAM_ID, STAKE_SEED, ESCROW_SEED } from './constants'

/**
 * Derive the stake account PDA for a user and tier.
 */
export function deriveStakePda(
  owner: PublicKey,
  tier: number
): [PublicKey, number] {
  const programId = new PublicKey(HOPIUM_PROGRAM_ID)

  return PublicKey.findProgramAddressSync(
    [
      Buffer.from(STAKE_SEED),
      owner.toBuffer(),
      Buffer.from([tier]),
    ],
    programId
  )
}

/**
 * Derive the escrow authority PDA.
 */
export function deriveEscrowAuthority(): [PublicKey, number] {
  const programId = new PublicKey(HOPIUM_PROGRAM_ID)

  return PublicKey.findProgramAddressSync(
    [Buffer.from(ESCROW_SEED)],
    programId
  )
}

/**
 * Check if a stake PDA exists for a user/tier combo.
 * Returns the PDA address string.
 */
export function getStakePdaAddress(
  owner: PublicKey | string,
  tier: number
): string {
  const ownerPk = typeof owner === 'string' ? new PublicKey(owner) : owner
  const [pda] = deriveStakePda(ownerPk, tier)
  return pda.toBase58()
}
