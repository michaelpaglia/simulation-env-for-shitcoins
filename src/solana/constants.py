"""Solana program constants and configuration."""

import os
from typing import Final

# Program and token addresses (loaded from environment)
HOPIUM_PROGRAM_ID: Final[str] = os.getenv(
    "HOPIUM_PROGRAM_ID",
    "7xUNHtezv3M6uxMfKRG8JNQYafMtJp9dSqAYJHP1fx8F"
)

HOPIUM_MINT_ADDRESS: Final[str] = os.getenv(
    "HOPIUM_MINT_ADDRESS",
    "HopiumMint11111111111111111111111111111111111"  # Placeholder
)

# RPC endpoint
SOLANA_RPC_URL: Final[str] = os.getenv(
    "SOLANA_RPC_URL",
    "https://api.devnet.solana.com"
)

# Stake tiers: (amount in base units, lock seconds, sim hours)
# Assuming 6 decimals for the token
STAKE_TIERS: Final[dict[int, dict]] = {
    0: {"amount": 100_000_000, "lock_days": 7, "sim_hours": 12},   # 100 tokens
    1: {"amount": 500_000_000, "lock_days": 3, "sim_hours": 24},   # 500 tokens
    2: {"amount": 1_000_000_000, "lock_days": 1, "sim_hours": 48}, # 1000 tokens
}

# Convert tiers to amount lookup
TIER_AMOUNTS: Final[dict[int, int]] = {
    tier: data["amount"] for tier, data in STAKE_TIERS.items()
}

# Burn rate in basis points (500 = 5%)
BURN_RATE_BPS: Final[int] = 500

# Emergency penalty in basis points (3000 = 30%)
EMERGENCY_PENALTY_BPS: Final[int] = 3000

# PDA seeds
STAKE_SEED: Final[bytes] = b"stake"
ESCROW_SEED: Final[bytes] = b"escrow"
