"""Solana integration for on-chain stake verification."""

from .client import SolanaClient
from .stake_verifier import StakeVerifier
from .constants import (
    HOPIUM_PROGRAM_ID,
    HOPIUM_MINT_ADDRESS,
    STAKE_TIERS,
    BURN_RATE_BPS,
)

__all__ = [
    "SolanaClient",
    "StakeVerifier",
    "HOPIUM_PROGRAM_ID",
    "HOPIUM_MINT_ADDRESS",
    "STAKE_TIERS",
    "BURN_RATE_BPS",
]
