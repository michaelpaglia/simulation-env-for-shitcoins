"""Stake verification service for simulation access control."""

import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from .client import SolanaClient, StakeAccountData
from .constants import (
    HOPIUM_MINT_ADDRESS,
    STAKE_TIERS,
    TIER_AMOUNTS,
)

logger = logging.getLogger(__name__)


class StakeError(Enum):
    """Stake verification error types."""
    NOT_FOUND = "stake_not_found"
    ALREADY_USED = "stake_already_used"
    WRONG_OWNER = "wrong_owner"
    WRONG_TIER = "wrong_tier"
    INSUFFICIENT_AMOUNT = "insufficient_amount"
    INVALID_PDA = "invalid_pda"


@dataclass
class StakeVerification:
    """Result of stake verification."""
    valid: bool
    stake_pda: Optional[str] = None
    tier: Optional[int] = None
    amount: Optional[int] = None
    sim_hours: Optional[int] = None
    error: Optional[StakeError] = None
    message: Optional[str] = None


@dataclass
class WalletStakeStatus:
    """Stake status for a wallet."""
    wallet: str
    token_balance: int
    stakes: list[dict]
    available_tiers: list[int]


class StakeVerifier:
    """Verify on-chain stakes for simulation access."""

    def __init__(self, client: Optional[SolanaClient] = None):
        self.client = client or SolanaClient()

    async def verify_stake(
        self,
        wallet: str,
        stake_pda: str,
        required_tier: Optional[int] = None,
    ) -> StakeVerification:
        """Verify a stake is valid for simulation.

        Args:
            wallet: Owner wallet public key
            stake_pda: Stake account PDA address
            required_tier: Optional tier requirement

        Returns:
            StakeVerification result
        """
        try:
            # Fetch stake account
            stake = await self.client.get_stake_account(stake_pda)
            if not stake:
                return StakeVerification(
                    valid=False,
                    error=StakeError.NOT_FOUND,
                    message="Stake account not found on-chain",
                )

            # Verify owner matches
            # Note: In production, properly compare pubkeys
            # This is simplified for demo
            if stake.owner != wallet:
                return StakeVerification(
                    valid=False,
                    error=StakeError.WRONG_OWNER,
                    message="Stake account owner does not match wallet",
                )

            # Check if already used
            if stake.simulation_used:
                return StakeVerification(
                    valid=False,
                    stake_pda=stake_pda,
                    tier=stake.tier,
                    error=StakeError.ALREADY_USED,
                    message=f"Stake already used for simulation: {stake.simulation_id}",
                )

            # Verify tier if required
            if required_tier is not None and stake.tier != required_tier:
                return StakeVerification(
                    valid=False,
                    stake_pda=stake_pda,
                    tier=stake.tier,
                    error=StakeError.WRONG_TIER,
                    message=f"Stake tier {stake.tier} does not match required {required_tier}",
                )

            # Verify amount matches tier
            expected_amount = TIER_AMOUNTS.get(stake.tier)
            if expected_amount and stake.amount < expected_amount:
                return StakeVerification(
                    valid=False,
                    stake_pda=stake_pda,
                    tier=stake.tier,
                    amount=stake.amount,
                    error=StakeError.INSUFFICIENT_AMOUNT,
                    message=f"Stake amount {stake.amount} less than tier requirement {expected_amount}",
                )

            # Get simulation hours for this tier
            tier_config = STAKE_TIERS.get(stake.tier, {})
            sim_hours = tier_config.get("sim_hours", 24)

            return StakeVerification(
                valid=True,
                stake_pda=stake_pda,
                tier=stake.tier,
                amount=stake.amount,
                sim_hours=sim_hours,
            )

        except Exception as e:
            logger.exception(f"Stake verification failed: {e}")
            return StakeVerification(
                valid=False,
                error=StakeError.INVALID_PDA,
                message=f"Failed to verify stake: {str(e)}",
            )

    async def get_wallet_status(self, wallet: str) -> WalletStakeStatus:
        """Get all stake information for a wallet.

        Args:
            wallet: Wallet public key

        Returns:
            WalletStakeStatus with balance and all stakes
        """
        # Get token balance
        balance = await self.client.get_token_balance(wallet, HOPIUM_MINT_ADDRESS)

        # Find all stake PDAs for this wallet
        stakes = []
        for tier in range(3):
            pda = await self.client.get_stake_pda(wallet, tier)
            stake = await self.client.get_stake_account(pda)
            if stake:
                tier_config = STAKE_TIERS.get(tier, {})
                stakes.append({
                    "pda": pda,
                    "tier": tier,
                    "amount": stake.amount,
                    "staked_at": stake.staked_at.isoformat(),
                    "unlock_at": stake.unlock_at.isoformat(),
                    "simulation_used": stake.simulation_used,
                    "simulation_id": stake.simulation_id or None,
                    "burned": stake.burned,
                    "can_release": stake.can_release,
                    "is_locked": stake.is_locked,
                    "sim_hours": tier_config.get("sim_hours", 24),
                })

        # Determine which tiers are available (not already staked)
        staked_tiers = {s["tier"] for s in stakes if not s["can_release"]}
        available_tiers = [t for t in range(3) if t not in staked_tiers]

        return WalletStakeStatus(
            wallet=wallet,
            token_balance=balance,
            stakes=stakes,
            available_tiers=available_tiers,
        )

    async def can_afford_tier(self, wallet: str, tier: int) -> tuple[bool, int]:
        """Check if wallet can afford a stake tier.

        Args:
            wallet: Wallet public key
            tier: Tier to check (0, 1, or 2)

        Returns:
            Tuple of (can_afford, current_balance)
        """
        balance = await self.client.get_token_balance(wallet, HOPIUM_MINT_ADDRESS)
        required = TIER_AMOUNTS.get(tier, 0)
        return balance >= required, balance
