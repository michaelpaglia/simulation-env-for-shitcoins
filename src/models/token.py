"""Token model - defines a shitcoin for simulation."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MarketCondition(str, Enum):
    BEAR = "bear"
    CRAB = "crab"
    BULL = "bull"
    EUPHORIA = "euphoria"


class MemeStyle(str, Enum):
    CUTE = "cute"  # Doge, cats, wholesome
    EDGY = "edgy"  # Dark humor, offensive
    ABSURD = "absurd"  # Random, surreal
    TOPICAL = "topical"  # Current events, trending
    NOSTALGIC = "nostalgic"  # Retro, throwback


class Token(BaseModel):
    """A shitcoin configuration for simulation."""

    name: str = Field(..., description="Full token name")
    ticker: str = Field(..., max_length=10, description="Token ticker symbol")
    narrative: str = Field(..., description="The story/hook - why should anyone care?")

    meme_style: MemeStyle = Field(default=MemeStyle.ABSURD, description="Type of meme aesthetic")
    tagline: Optional[str] = Field(default=None, description="One-liner catchphrase")

    # Market context
    market_condition: MarketCondition = Field(default=MarketCondition.CRAB)
    competing_narratives: list[str] = Field(default_factory=list, description="Other hot tokens right now")

    # Launch params (for context)
    initial_liquidity_usd: float = Field(default=10000, description="Starting liquidity")

    def get_pitch(self) -> str:
        """Generate the elevator pitch for this token."""
        pitch = f"${self.ticker} - {self.name}\n"
        pitch += f"Narrative: {self.narrative}\n"
        if self.tagline:
            pitch += f"Tagline: {self.tagline}\n"
        pitch += f"Vibe: {self.meme_style.value}"
        return pitch


class SimulationResult(BaseModel):
    """Results from a simulation run."""

    token: Token

    # Core metrics
    viral_coefficient: float = Field(..., ge=0, description="New users per existing user")
    peak_sentiment: float = Field(..., ge=-1, le=1, description="-1 (max FUD) to 1 (max hype)")
    sentiment_stability: float = Field(..., ge=0, le=1, description="How steady the sentiment stays")
    fud_resistance: float = Field(..., ge=0, le=1, description="How well it survives skeptics")

    # Engagement
    total_mentions: int
    total_engagement: int  # likes + retweets + replies
    influencer_pickups: int

    # Timeline
    hours_to_peak: int
    hours_to_death: Optional[int] = None  # None if still alive

    # Qualitative
    dominant_narrative: str  # What CT ended up calling it
    top_fud_points: list[str]  # Main criticisms

    # Prediction
    predicted_outcome: str  # "rug", "pump_and_dump", "slow_bleed", "moon", "cult_classic"
    confidence: float = Field(..., ge=0, le=1)

    def summary(self) -> str:
        """Generate a human-readable summary."""
        return f"""
=== SIMULATION RESULTS: ${self.token.ticker} ===

VIRAL SCORE: {self.viral_coefficient:.2f}x
SENTIMENT: {self.peak_sentiment:+.2f} peak | {self.sentiment_stability:.0%} stable
FUD RESISTANCE: {self.fud_resistance:.0%}

ENGAGEMENT:
- {self.total_mentions} mentions
- {self.total_engagement} total engagement
- {self.influencer_pickups} influencer pickups

TIMELINE:
- Peak hype at hour {self.hours_to_peak}
- {"Still alive" if not self.hours_to_death else f"Dead by hour {self.hours_to_death}"}

CT VERDICT: "{self.dominant_narrative}"

TOP FUD:
{chr(10).join(f"- {fud}" for fud in self.top_fud_points[:3])}

PREDICTION: {self.predicted_outcome.upper()} ({self.confidence:.0%} confidence)
"""
