"""Tests for token and result models."""

import pytest
from pydantic import ValidationError
from src.models.token import Token, SimulationResult, MarketCondition, MemeStyle


class TestTokenModel:
    """Tests for Token model validation and behavior."""

    def test_token_creation_minimal(self):
        """Token can be created with minimal required fields."""
        token = Token(
            name="TestCoin",
            ticker="TEST",
            narrative="A test narrative",
        )
        assert token.name == "TestCoin"
        assert token.ticker == "TEST"
        assert token.narrative == "A test narrative"
        # Defaults
        assert token.meme_style == MemeStyle.ABSURD
        assert token.market_condition == MarketCondition.CRAB

    def test_token_creation_full(self):
        """Token can be created with all fields."""
        token = Token(
            name="FullCoin",
            ticker="FULL",
            narrative="Complete narrative",
            tagline="To the moon",
            meme_style=MemeStyle.EDGY,
            market_condition=MarketCondition.BULL,
            initial_liquidity_usd=50000,
            competing_narratives=["DOGE", "SHIB"],
        )
        assert token.tagline == "To the moon"
        assert token.meme_style == MemeStyle.EDGY
        assert token.market_condition == MarketCondition.BULL
        assert token.initial_liquidity_usd == 50000
        assert len(token.competing_narratives) == 2

    def test_token_ticker_max_length(self):
        """Ticker should respect max length."""
        token = Token(
            name="Test",
            ticker="ABCDEFGHIJ",  # 10 chars - at limit
            narrative="Test",
        )
        assert len(token.ticker) == 10

    def test_token_get_pitch(self, sample_token):
        """get_pitch() returns formatted string."""
        pitch = sample_token.get_pitch()
        assert "$TEST" in pitch
        assert "TestCoin" in pitch
        assert "test token" in pitch.lower()

    def test_all_market_conditions(self):
        """All market conditions are valid."""
        for condition in MarketCondition:
            token = Token(
                name="Test",
                ticker="TEST",
                narrative="Test",
                market_condition=condition,
            )
            assert token.market_condition == condition

    def test_all_meme_styles(self):
        """All meme styles are valid."""
        for style in MemeStyle:
            token = Token(
                name="Test",
                ticker="TEST",
                narrative="Test",
                meme_style=style,
            )
            assert token.meme_style == style


class TestSimulationResult:
    """Tests for SimulationResult model."""

    def test_result_creation(self, sample_token):
        """SimulationResult can be created with valid data."""
        result = SimulationResult(
            token=sample_token,
            viral_coefficient=1.5,
            peak_sentiment=0.7,
            sentiment_stability=0.8,
            fud_resistance=0.6,
            total_mentions=100,
            total_engagement=5000,
            influencer_pickups=3,
            hours_to_peak=12,
            hours_to_death=None,
            dominant_narrative="Hidden gem",
            top_fud_points=["Anon team", "Low liquidity"],
            predicted_outcome="cult_classic",
            confidence=0.65,
        )
        assert result.viral_coefficient == 1.5
        assert result.predicted_outcome == "cult_classic"

    def test_result_sentiment_bounds(self, sample_token):
        """Sentiment values must be within bounds."""
        # Valid: -1 to 1
        result = SimulationResult(
            token=sample_token,
            viral_coefficient=1.0,
            peak_sentiment=1.0,  # Max
            sentiment_stability=0.5,
            fud_resistance=0.5,
            total_mentions=10,
            total_engagement=100,
            influencer_pickups=0,
            hours_to_peak=1,
            dominant_narrative="Test",
            top_fud_points=[],
            predicted_outcome="moon",
            confidence=0.5,
        )
        assert result.peak_sentiment == 1.0

        # Test -1
        result2 = SimulationResult(
            token=sample_token,
            viral_coefficient=1.0,
            peak_sentiment=-1.0,  # Min
            sentiment_stability=0.5,
            fud_resistance=0.5,
            total_mentions=10,
            total_engagement=100,
            influencer_pickups=0,
            hours_to_peak=1,
            dominant_narrative="Test",
            top_fud_points=[],
            predicted_outcome="rug",
            confidence=0.5,
        )
        assert result2.peak_sentiment == -1.0

    def test_result_summary_generation(self, sample_token):
        """summary() generates readable output."""
        result = SimulationResult(
            token=sample_token,
            viral_coefficient=1.5,
            peak_sentiment=0.7,
            sentiment_stability=0.8,
            fud_resistance=0.6,
            total_mentions=100,
            total_engagement=5000,
            influencer_pickups=3,
            hours_to_peak=12,
            hours_to_death=None,
            dominant_narrative="Hidden gem",
            top_fud_points=["Anon team"],
            predicted_outcome="cult_classic",
            confidence=0.65,
        )
        summary = result.summary()
        assert "TEST" in summary
        assert "1.50" in summary  # viral coefficient
        assert "CULT_CLASSIC" in summary

    def test_result_with_death_hour(self, sample_token):
        """Result can track when token died."""
        result = SimulationResult(
            token=sample_token,
            viral_coefficient=0.3,
            peak_sentiment=-0.5,
            sentiment_stability=0.2,
            fud_resistance=0.1,
            total_mentions=20,
            total_engagement=200,
            influencer_pickups=0,
            hours_to_peak=2,
            hours_to_death=18,  # Died at hour 18
            dominant_narrative="Rug confirmed",
            top_fud_points=["Dev sold", "Honeypot"],
            predicted_outcome="rug",
            confidence=0.8,
        )
        assert result.hours_to_death == 18
        summary = result.summary()
        assert "18" in summary


class TestDataValidation:
    """Tests for data validation edge cases."""

    def test_empty_narrative(self):
        """Empty narrative should still work."""
        token = Token(
            name="Test",
            ticker="TEST",
            narrative="",  # Empty but valid
        )
        assert token.narrative == ""

    def test_unicode_in_token(self):
        """Unicode characters should be handled."""
        token = Token(
            name="🚀 MoonCoin 🌙",
            ticker="MOON",
            narrative="To the moon! 🚀🌙✨",
            tagline="Diamond hands 💎🙌",
        )
        assert "🚀" in token.name
        assert "🚀" in token.narrative

    def test_special_characters_in_ticker(self):
        """Ticker with numbers is valid."""
        token = Token(
            name="Test",
            ticker="TEST123",
            narrative="Test",
        )
        assert token.ticker == "TEST123"

    def test_large_liquidity_value(self):
        """Large liquidity values should work."""
        token = Token(
            name="Test",
            ticker="TEST",
            narrative="Test",
            initial_liquidity_usd=1_000_000_000,  # 1 billion
        )
        assert token.initial_liquidity_usd == 1_000_000_000

    def test_many_competing_narratives(self):
        """Many competing narratives should work."""
        token = Token(
            name="Test",
            ticker="TEST",
            narrative="Test",
            competing_narratives=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        )
        assert len(token.competing_narratives) == 10
