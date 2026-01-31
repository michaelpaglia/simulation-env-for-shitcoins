/**
 * Transaction instruction builders for HOPIUM staking.
 *
 * Note: These are placeholder implementations. In production,
 * you would use the Anchor-generated IDL and client library.
 */

import {
  Connection,
  PublicKey,
  Transaction,
  TransactionInstruction,
  SystemProgram,
} from '@solana/web3.js'
import {
  TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  createAssociatedTokenAccountInstruction,
} from '@solana/spl-token'
import { HOPIUM_PROGRAM_ID, HOPIUM_MINT_ADDRESS, STAKE_TIERS, StakeTier } from './constants'
import { deriveStakePda, deriveEscrowAuthority } from './pda'

// Instruction discriminators (first 8 bytes of sha256 of instruction name)
// These would come from the Anchor IDL in production
const INSTRUCTION_DISCRIMINATORS = {
  stake: Buffer.from([206, 176, 202, 18, 200, 209, 179, 108]),
  emergencyWithdraw: Buffer.from([158, 71, 215, 97, 210, 22, 106, 23]),
  release: Buffer.from([154, 49, 206, 38, 4, 112, 144, 85]),
}

/**
 * Build a stake transaction.
 */
export async function buildStakeTransaction(
  connection: Connection,
  owner: PublicKey,
  tier: StakeTier,
  escrowTokenAccount: PublicKey
): Promise<Transaction> {
  const programId = new PublicKey(HOPIUM_PROGRAM_ID)
  const tokenMint = new PublicKey(HOPIUM_MINT_ADDRESS)

  // Derive PDAs
  const [stakePda, stakeBump] = deriveStakePda(owner, tier)

  // Get user's token account
  const userTokenAccount = await getAssociatedTokenAddress(tokenMint, owner)

  // Build instruction data: discriminator + tier (u8)
  const data = Buffer.alloc(9)
  INSTRUCTION_DISCRIMINATORS.stake.copy(data, 0)
  data.writeUInt8(tier, 8)

  // Build instruction
  const instruction = new TransactionInstruction({
    programId,
    keys: [
      { pubkey: owner, isSigner: true, isWritable: true },
      { pubkey: stakePda, isSigner: false, isWritable: true },
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
      { pubkey: tokenMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data,
  })

  const transaction = new Transaction()
  transaction.add(instruction)

  // Get recent blockhash
  const { blockhash } = await connection.getLatestBlockhash()
  transaction.recentBlockhash = blockhash
  transaction.feePayer = owner

  return transaction
}

/**
 * Build an emergency withdraw transaction.
 */
export async function buildEmergencyWithdrawTransaction(
  connection: Connection,
  owner: PublicKey,
  tier: number,
  escrowTokenAccount: PublicKey
): Promise<Transaction> {
  const programId = new PublicKey(HOPIUM_PROGRAM_ID)
  const tokenMint = new PublicKey(HOPIUM_MINT_ADDRESS)

  // Derive PDAs
  const [stakePda] = deriveStakePda(owner, tier)
  const [escrowAuthority] = deriveEscrowAuthority()

  // Get user's token account
  const userTokenAccount = await getAssociatedTokenAddress(tokenMint, owner)

  // Build instruction
  const instruction = new TransactionInstruction({
    programId,
    keys: [
      { pubkey: owner, isSigner: true, isWritable: true },
      { pubkey: stakePda, isSigner: false, isWritable: true },
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
      { pubkey: tokenMint, isSigner: false, isWritable: true },
      { pubkey: escrowAuthority, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data: INSTRUCTION_DISCRIMINATORS.emergencyWithdraw,
  })

  const transaction = new Transaction()
  transaction.add(instruction)

  const { blockhash } = await connection.getLatestBlockhash()
  transaction.recentBlockhash = blockhash
  transaction.feePayer = owner

  return transaction
}

/**
 * Build a release stake transaction (after lock period).
 */
export async function buildReleaseTransaction(
  connection: Connection,
  owner: PublicKey,
  tier: number,
  escrowTokenAccount: PublicKey
): Promise<Transaction> {
  const programId = new PublicKey(HOPIUM_PROGRAM_ID)

  // Derive PDAs
  const [stakePda] = deriveStakePda(owner, tier)
  const [escrowAuthority] = deriveEscrowAuthority()
  const tokenMint = new PublicKey(HOPIUM_MINT_ADDRESS)

  // Get user's token account
  const userTokenAccount = await getAssociatedTokenAddress(tokenMint, owner)

  // Build instruction
  const instruction = new TransactionInstruction({
    programId,
    keys: [
      { pubkey: owner, isSigner: true, isWritable: true },
      { pubkey: stakePda, isSigner: false, isWritable: true },
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
      { pubkey: escrowAuthority, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data: INSTRUCTION_DISCRIMINATORS.release,
  })

  const transaction = new Transaction()
  transaction.add(instruction)

  const { blockhash } = await connection.getLatestBlockhash()
  transaction.recentBlockhash = blockhash
  transaction.feePayer = owner

  return transaction
}

/**
 * Check if a token account exists, create ATA instruction if not.
 */
export async function ensureTokenAccountInstruction(
  connection: Connection,
  owner: PublicKey,
  mint: PublicKey = new PublicKey(HOPIUM_MINT_ADDRESS)
): Promise<TransactionInstruction | null> {
  const ata = await getAssociatedTokenAddress(mint, owner)

  try {
    await connection.getAccountInfo(ata)
    return null // Account exists
  } catch {
    // Create ATA instruction
    return createAssociatedTokenAccountInstruction(owner, ata, owner, mint)
  }
}
