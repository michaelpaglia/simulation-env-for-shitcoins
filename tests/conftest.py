"""Pytest fixtures for simulation tests."""

import pytest
from src.models.token import Token, MarketCondition, MemeStyle
from src.agents.personas import Persona, PersonaType, get_all_personas, PERSONAS, KOLS
from src.simulation.engine import SimulationEngine, SimulationState


@pytest.fixture
def sample_token():
    """Create a sample token for testing."""
    return Token(
        name="TestCoin",
        ticker="TEST",
        narrative="A test token for unit testing",
        tagline="Testing the moon",
        meme_style=MemeStyle.ABSURD,
        market_condition=MarketCondition.CRAB,
    )


@pytest.fixture
def bull_market_token():
    """Token in bull market conditions."""
    return Token(
        name="BullToken",
        ticker="BULL",
        narrative="Bull market test token",
        market_condition=MarketCondition.BULL,
    )


@pytest.fixture
def bear_market_token():
    """Token in bear market conditions."""
    return Token(
        name="BearToken",
        ticker="BEAR",
        narrative="Bear market test token",
        market_condition=MarketCondition.BEAR,
    )


@pytest.fixture
def simulation_engine():
    """Create simulation engine without API key (template mode)."""
    return SimulationEngine(api_key=None)


@pytest.fixture
def empty_state(sample_token):
    """Create empty simulation state."""
    return SimulationState(token=sample_token)


@pytest.fixture
def active_state(sample_token):
    """Create simulation state with some activity."""
    state = SimulationState(token=sample_token)
    state.awareness = 0.5
    state.momentum = 0.3
    state.current_hour = 10
    state.total_mentions = 50
    state.total_engagement = 5000
    return state


@pytest.fixture
def all_personas():
    """Get all personas including KOLs."""
    return get_all_personas(include_kols=True)


@pytest.fixture
def degen_persona():
    """Get degen persona."""
    return PERSONAS[PersonaType.DEGEN]


@pytest.fixture
def skeptic_persona():
    """Get skeptic persona."""
    return PERSONAS[PersonaType.SKEPTIC]


@pytest.fixture
def whale_persona():
    """Get whale persona."""
    return PERSONAS[PersonaType.WHALE]
