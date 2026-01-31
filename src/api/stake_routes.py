"""API routes for stake verification and management."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..solana import StakeVerifier, STAKE_TIERS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stake", tags=["stake"])

# Shared verifier instance
_verifier: Optional[StakeVerifier] = None


def get_verifier() -> StakeVerifier:
    """Get or create the stake verifier instance."""
    global _verifier
    if _verifier is None:
        _verifier = StakeVerifier()
    return _verifier


# Request/Response Models

class VerifyStakeRequest(BaseModel):
    """Request to verify a stake for simulation access."""
    wallet: str = Field(..., description="Wallet public key (base58)")
    stake_pda: str = Field(..., description="Stake account PDA address")
    tier: Optional[int] = Field(default=None, ge=0, le=2, description="Required tier (0-2)")


class VerifyStakeResponse(BaseModel):
    """Response from stake verification."""
    valid: bool
    stake_pda: Optional[str] = None
    tier: Optional[int] = None
    amount: Optional[int] = None
    sim_hours: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None


class StakeInfo(BaseModel):
    """Information about a single stake."""
    pda: str
    tier: int
    amount: int
    staked_at: str
    unlock_at: str
    simulation_used: bool
    simulation_id: Optional[str] = None
    burned: bool
    can_release: bool
    is_locked: bool
    sim_hours: int


class WalletStatusResponse(BaseModel):
    """Response with wallet stake status."""
    wallet: str
    token_balance: int
    token_balance_display: str
    stakes: list[StakeInfo]
    available_tiers: list[int]


class TierInfo(BaseModel):
    """Information about a stake tier."""
    tier: int
    amount: int
    amount_display: str
    lock_days: int
    sim_hours: int


class TiersResponse(BaseModel):
    """Response listing all stake tiers."""
    tiers: list[TierInfo]


# Routes

@router.post("/verify", response_model=VerifyStakeResponse)
async def verify_stake(request: VerifyStakeRequest):
    """Verify a stake is valid for simulation access.

    This endpoint checks:
    - Stake account exists on-chain
    - Stake is owned by the wallet
    - Stake has not been used for a simulation
    - Stake meets tier requirements
    """
    verifier = get_verifier()
    result = await verifier.verify_stake(
        wallet=request.wallet,
        stake_pda=request.stake_pda,
        required_tier=request.tier,
    )

    return VerifyStakeResponse(
        valid=result.valid,
        stake_pda=result.stake_pda,
        tier=result.tier,
        amount=result.amount,
        sim_hours=result.sim_hours,
        error=result.error.value if result.error else None,
        message=result.message,
    )


@router.get("/status/{wallet}", response_model=WalletStatusResponse)
async def get_wallet_status(wallet: str):
    """Get stake status for a wallet.

    Returns:
    - Token balance
    - All active stakes with their status
    - Available tiers for new stakes
    """
    verifier = get_verifier()

    try:
        status = await verifier.get_wallet_status(wallet)
    except Exception as e:
        logger.exception(f"Failed to get wallet status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch wallet status: {str(e)}",
        )

    # Convert balance to display format (assuming 6 decimals)
    balance_display = f"{status.token_balance / 1_000_000:.2f}"

    return WalletStatusResponse(
        wallet=status.wallet,
        token_balance=status.token_balance,
        token_balance_display=balance_display,
        stakes=[StakeInfo(**s) for s in status.stakes],
        available_tiers=status.available_tiers,
    )


@router.get("/tiers", response_model=TiersResponse)
async def get_stake_tiers():
    """Get all available stake tiers and their requirements."""
    tiers = []
    for tier_id, config in STAKE_TIERS.items():
        amount_display = f"{config['amount'] / 1_000_000:.0f}"
        tiers.append(TierInfo(
            tier=tier_id,
            amount=config["amount"],
            amount_display=amount_display,
            lock_days=config["lock_days"],
            sim_hours=config["sim_hours"],
        ))

    return TiersResponse(tiers=tiers)


@router.get("/can-afford/{wallet}/{tier}")
async def check_affordability(wallet: str, tier: int):
    """Check if a wallet can afford a specific tier.

    Returns whether the wallet has sufficient token balance
    to stake for the requested tier.
    """
    if tier < 0 or tier > 2:
        raise HTTPException(status_code=400, detail="Tier must be 0, 1, or 2")

    verifier = get_verifier()
    can_afford, balance = await verifier.can_afford_tier(wallet, tier)

    tier_config = STAKE_TIERS.get(tier, {})
    required = tier_config.get("amount", 0)

    return {
        "can_afford": can_afford,
        "balance": balance,
        "balance_display": f"{balance / 1_000_000:.2f}",
        "required": required,
        "required_display": f"{required / 1_000_000:.0f}",
        "tier": tier,
    }
