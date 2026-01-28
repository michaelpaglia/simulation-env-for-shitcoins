"""Pre-configured token templates for common archetypes."""

from typing import Optional
from ..models.token import Token, MemeStyle, MarketCondition


# Preset definitions with metadata
_PRESET_DATA = {
    "doge": {
        "token": Token(
            name="Classic Dog Coin",
            ticker="DOGE",
            narrative="The OG dog coin energy - much wow, very gains, so community",
            meme_style=MemeStyle.CUTE,
            tagline="such gains, very moon",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["cat coins", "other dog coins"],
        ),
        "description": "Classic Doge-style dog coin with wholesome community vibes",
        "category": "animal",
    },
    "ai": {
        "token": Token(
            name="AI Agent Token",
            ticker="AGENT",
            narrative="Autonomous AI agent managing its own treasury - the future of crypto",
            meme_style=MemeStyle.TOPICAL,
            tagline="AI that trades for you",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["other AI tokens", "GPT coins"],
        ),
        "description": "AI/autonomous agent narrative riding the AI hype wave",
        "category": "tech",
    },
    "pepe": {
        "token": Token(
            name="Frog Meme Coin",
            ticker="PEPE",
            narrative="Feels good man - the iconic frog returns to claim the throne",
            meme_style=MemeStyle.NOSTALGIC,
            tagline="feels good man",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["other frog coins", "wojak"],
        ),
        "description": "Nostalgic Pepe frog meme with classic meme culture appeal",
        "category": "meme",
    },
    "cat": {
        "token": Token(
            name="Cat Supremacy",
            ticker="CAT",
            narrative="Dogs had their day - cats are taking over crypto Twitter",
            meme_style=MemeStyle.CUTE,
            tagline="meow money meow problems",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["dog coins", "other cat coins"],
        ),
        "description": "Cat coin meta play - cute aesthetic, anti-dog narrative",
        "category": "animal",
    },
    "edgy": {
        "token": Token(
            name="Dark Humor Coin",
            ticker="EDGE",
            narrative="Too edgy for normies - if you know you know",
            meme_style=MemeStyle.EDGY,
            tagline="we do a little trolling",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["normie coins"],
        ),
        "description": "Edgy/dark humor aesthetic for degen audiences",
        "category": "culture",
    },
    "meta": {
        "token": Token(
            name="Self-Aware Token",
            ticker="META",
            narrative="A token about tokens - we're all just exit liquidity anyway",
            meme_style=MemeStyle.ABSURD,
            tagline="the real token was the friends we rugged along the way",
            market_condition=MarketCondition.CRAB,
            competing_narratives=["serious projects"],
        ),
        "description": "Ironic, self-referential meta commentary on crypto culture",
        "category": "culture",
    },
}

# Extract just the Token objects for easy access
PRESETS: dict[str, Token] = {
    name: data["token"] for name, data in _PRESET_DATA.items()
}


def get_preset(name: str, ticker_override: Optional[str] = None) -> Token:
    """Get a preset token template.

    Args:
        name: Preset name (doge, ai, pepe, cat, edgy, meta)
        ticker_override: Optional custom ticker to use instead of default

    Returns:
        Token configured with preset values

    Raises:
        ValueError: If preset name is not found
    """
    name_lower = name.lower()
    if name_lower not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")

    token = PRESETS[name_lower].model_copy()

    if ticker_override:
        token.ticker = ticker_override.upper()[:10]

    return token


def list_presets() -> list[str]:
    """List all available preset names."""
    return list(PRESETS.keys())


def get_preset_info(name: str) -> dict:
    """Get detailed info about a preset.

    Args:
        name: Preset name

    Returns:
        Dict with token, description, and category

    Raises:
        ValueError: If preset name is not found
    """
    name_lower = name.lower()
    if name_lower not in _PRESET_DATA:
        available = ", ".join(_PRESET_DATA.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")

    return _PRESET_DATA[name_lower]
