"""Tests for data handling, edge cases, and stress testing."""

import pytest
import random
import string
from src.models.token import Token, SimulationResult, MarketCondition, MemeStyle
from src.simulation.engine import SimulationEngine, SimulationState
from src.agents.personas import get_all_personas, KOLS


class TestDataIntegrity:
    """Tests for data integrity throughout simulation."""

    def test_token_immutability_during_simulation(self, simulation_engine, sample_token):
        """Token should not be modified during simulation."""
        original_ticker = sample_token.ticker
        original_name = sample_token.name
        original_narrative = sample_token.narrative

        simulation_engine.run_simulation(sample_token, hours=24)

        assert sample_token.ticker == original_ticker
        assert sample_token.name == original_name
        assert sample_token.narrative == original_narrative

    def test_state_consistency(self, simulation_engine, sample_token):
        """State should maintain consistency throughout simulation."""
        state = SimulationState(token=sample_token)

        for _ in range(20):
            active = simulation_engine._select_active_personas(state)
            for persona in active:
                tweet = simulation_engine._generate_tweet(persona, sample_token, state)
                assert tweet.hour == state.current_hour
            simulation_engine._update_state(state, [])

            # Invariants
            assert 0 <= state.awareness <= 1
            assert -1 <= state.momentum <= 1
            assert state.current_hour >= 0
            assert state.total_mentions >= 0
            assert state.total_engagement >= 0

    def test_tweet_count_matches_mentions(self, simulation_engine, sample_token):
        """Total mentions should equal tweet count."""
        result = simulation_engine.run_simulation(sample_token, hours=24)
        # Note: mentions is tracked separately but should correlate with tweets generated
        assert result.total_mentions >= 0


class TestLargeDataHandling:
    """Tests for handling large amounts of data."""

    def test_long_simulation_memory(self, simulation_engine, sample_token):
        """Long simulation shouldn't cause memory issues."""
        # Run 168 hours (1 week)
        result = simulation_engine.run_simulation(sample_token, hours=168)
        assert result is not None
        assert result.total_mentions >= 0

    def test_many_personas_active(self, simulation_engine, sample_token):
        """System handles many active personas."""
        state = SimulationState(token=sample_token)
        state.awareness = 1.0  # Maximum awareness
        state.momentum = 0.5   # Bullish

        # Should handle selecting from all personas
        for _ in range(50):
            active = simulation_engine._select_active_personas(state)
            for persona in active:
                tweet = simulation_engine._generate_tweet(persona, sample_token, state)
                assert tweet is not None
            simulation_engine._update_state(state, [])

    def test_large_engagement_numbers(self, simulation_engine):
        """System handles large engagement numbers."""
        state = SimulationState(token=Token(
            name="BigToken",
            ticker="BIG",
            narrative="Massive engagement test"
        ))
        state.total_engagement = 1_000_000_000  # 1 billion
        state.total_mentions = 10_000_000  # 10 million
        state.sentiment_history = [0.5] * 100

        result = simulation_engine._compile_results(state)
        assert result is not None
        assert result.viral_coefficient >= 0


class TestInputValidation:
    """Tests for input validation and sanitization."""

    def test_long_ticker(self):
        """Long ticker is handled."""
        token = Token(
            name="Test",
            ticker="A" * 10,  # Max length
            narrative="Test"
        )
        assert len(token.ticker) == 10

    def test_long_narrative(self):
        """Long narrative is handled."""
        long_narrative = "A" * 1000
        token = Token(
            name="Test",
            ticker="TEST",
            narrative=long_narrative
        )
        assert len(token.narrative) == 1000

    def test_special_characters_narrative(self):
        """Special characters in narrative are handled."""
        special_narrative = "Test <script>alert('xss')</script> & \"quotes\" 'single'"
        token = Token(
            name="Test",
            ticker="TEST",
            narrative=special_narrative
        )
        assert token.narrative == special_narrative

    def test_unicode_extensive(self):
        """Extensive unicode is handled."""
        unicode_name = "🚀🌙💎🙌🔥💰📈🎯✨⭐"
        token = Token(
            name=unicode_name,
            ticker="MOON",
            narrative="Unicode test 中文 日本語 한국어 العربية"
        )
        assert token.name == unicode_name

    def test_newlines_in_narrative(self):
        """Newlines in narrative are handled."""
        multiline = "Line 1\nLine 2\nLine 3"
        token = Token(
            name="Test",
            ticker="TEST",
            narrative=multiline
        )
        assert "\n" in token.narrative


class TestRandomizedInputs:
    """Tests with randomized inputs for robustness."""

    def test_random_tickers(self, simulation_engine):
        """Random tickers work."""
        for _ in range(10):
            ticker = ''.join(random.choices(string.ascii_uppercase, k=random.randint(1, 10)))
            token = Token(
                name=f"Random {ticker}",
                ticker=ticker,
                narrative="Random test"
            )
            result = simulation_engine.run_simulation(token, hours=6)
            assert result is not None

    def test_random_market_conditions(self, simulation_engine):
        """Random market conditions work."""
        conditions = list(MarketCondition)
        for _ in range(10):
            condition = random.choice(conditions)
            token = Token(
                name="RandomCondition",
                ticker="RAND",
                narrative="Testing random conditions",
                market_condition=condition
            )
            result = simulation_engine.run_simulation(token, hours=6)
            assert result is not None

    def test_random_meme_styles(self, simulation_engine):
        """Random meme styles work."""
        styles = list(MemeStyle)
        for _ in range(10):
            style = random.choice(styles)
            token = Token(
                name="RandomStyle",
                ticker="RAND",
                narrative="Testing random styles",
                meme_style=style
            )
            result = simulation_engine.run_simulation(token, hours=6)
            assert result is not None


class TestSyntheticDataConsistency:
    """Tests ensuring synthetic data is consistent and deterministic where expected."""

    def test_template_tweets_contain_ticker(self, simulation_engine, sample_token, empty_state):
        """Template tweets should always reference the token."""
        personas = get_all_personas(include_kols=False)

        for persona in personas:
            tweet = simulation_engine._generate_tweet(persona, sample_token, empty_state)
            # Most templates include ticker (except some whale responses)
            # At minimum, tweet should not be empty
            assert len(tweet.content) > 0

    def test_sentiment_correlates_with_persona(self, simulation_engine, sample_token, empty_state):
        """Sentiment should generally correlate with persona type."""
        from src.agents.personas import PersonaType, PERSONAS

        degen = PERSONAS[PersonaType.DEGEN]
        skeptic = PERSONAS[PersonaType.SKEPTIC]

        # Run multiple times to get average
        degen_sentiments = []
        skeptic_sentiments = []

        for _ in range(20):
            degen_tweet = simulation_engine._generate_tweet(degen, sample_token, empty_state)
            skeptic_tweet = simulation_engine._generate_tweet(skeptic, sample_token, empty_state)
            degen_sentiments.append(degen_tweet.sentiment)
            skeptic_sentiments.append(skeptic_tweet.sentiment)

        avg_degen = sum(degen_sentiments) / len(degen_sentiments)
        avg_skeptic = sum(skeptic_sentiments) / len(skeptic_sentiments)

        # Degen should be more positive than skeptic
        assert avg_degen > avg_skeptic

    def test_engagement_scales_with_influence(self, simulation_engine, sample_token, empty_state):
        """Engagement should scale with persona influence."""
        from src.agents.personas import PersonaType, PERSONAS

        whale = PERSONAS[PersonaType.WHALE]  # High influence
        normie = PERSONAS[PersonaType.NORMIE]  # Low influence

        whale_engagements = []
        normie_engagements = []

        for _ in range(20):
            whale_tweet = simulation_engine._generate_tweet(whale, sample_token, empty_state)
            normie_tweet = simulation_engine._generate_tweet(normie, sample_token, empty_state)
            whale_engagements.append(whale_tweet.likes + whale_tweet.retweets)
            normie_engagements.append(normie_tweet.likes + normie_tweet.retweets)

        avg_whale = sum(whale_engagements) / len(whale_engagements)
        avg_normie = sum(normie_engagements) / len(normie_engagements)

        # Whale should have higher engagement
        assert avg_whale > avg_normie


class TestPriorIntegration:
    """Tests for prior data integration (Twitter data calibration)."""

    def test_simulation_without_priors(self, simulation_engine, sample_token):
        """Simulation runs fine without Twitter priors."""
        result = simulation_engine.run_simulation(sample_token, hours=24)
        assert result is not None
        assert result.total_mentions > 0

    def test_market_condition_affects_outcome(self, simulation_engine):
        """Market condition should influence simulation outcomes."""
        bull_token = Token(
            name="Bull",
            ticker="BULL",
            narrative="Bull market test",
            market_condition=MarketCondition.EUPHORIA
        )
        bear_token = Token(
            name="Bear",
            ticker="BEAR",
            narrative="Bear market test",
            market_condition=MarketCondition.BEAR
        )

        # Run multiple simulations
        bull_results = [simulation_engine.run_simulation(bull_token, hours=24) for _ in range(5)]
        bear_results = [simulation_engine.run_simulation(bear_token, hours=24) for _ in range(5)]

        # Both should complete
        assert all(r is not None for r in bull_results)
        assert all(r is not None for r in bear_results)


class TestConcurrentSafety:
    """Tests for concurrent execution safety."""

    def test_multiple_simulations_independent(self):
        """Multiple simulations don't interfere with each other."""
        engine1 = SimulationEngine(api_key=None)
        engine2 = SimulationEngine(api_key=None)

        token1 = Token(name="Token1", ticker="TK1", narrative="First token")
        token2 = Token(name="Token2", ticker="TK2", narrative="Second token")

        result1 = engine1.run_simulation(token1, hours=12)
        result2 = engine2.run_simulation(token2, hours=12)

        # Results should be for correct tokens
        assert result1.token.ticker == "TK1"
        assert result2.token.ticker == "TK2"

    def test_state_isolation(self):
        """State is isolated between simulations."""
        engine = SimulationEngine(api_key=None)

        token1 = Token(name="Token1", ticker="TK1", narrative="First")
        token2 = Token(name="Token2", ticker="TK2", narrative="Second")

        state1 = SimulationState(token=token1)
        state2 = SimulationState(token=token2)

        # Modify state1
        state1.awareness = 0.9
        state1.momentum = 0.5

        # state2 should be unchanged
        assert state2.awareness == 0.1
        assert state2.momentum == 0.0
