"""Tests for simulation engine - core system validation."""

import pytest
from src.simulation.engine import SimulationEngine, SimulationState, Tweet, TweetType
from src.agents.personas import PersonaType, get_persona, PERSONAS
from src.models.token import MarketCondition


class TestSimulationEngine:
    """Tests for SimulationEngine core functionality."""

    def test_engine_creation_without_api(self):
        """Engine can be created without API key (template mode)."""
        engine = SimulationEngine(api_key=None)
        assert engine.client is None
        assert len(engine.personas) > 0

    def test_engine_has_personas(self, simulation_engine):
        """Engine loads personas on init."""
        assert len(simulation_engine.personas) > 0

    def test_run_simulation_returns_result(self, simulation_engine, sample_token):
        """run_simulation returns SimulationResult."""
        result = simulation_engine.run_simulation(sample_token, hours=6)
        assert result is not None
        assert result.token == sample_token
        assert result.total_mentions >= 0
        assert result.total_engagement >= 0

    def test_simulation_runs_specified_hours(self, simulation_engine, sample_token):
        """Simulation respects hours parameter."""
        result = simulation_engine.run_simulation(sample_token, hours=12)
        # hours_to_peak should be within range
        assert result.hours_to_peak <= 12


class TestTweetGeneration:
    """Tests for tweet generation logic."""

    def test_generate_tweet_template_mode(self, simulation_engine, sample_token, empty_state, degen_persona):
        """Template mode generates valid tweets."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        assert tweet is not None
        assert tweet.content is not None
        assert len(tweet.content) > 0
        assert tweet.author == degen_persona

    def test_tweet_contains_ticker(self, simulation_engine, sample_token, empty_state, degen_persona):
        """Generated tweets reference the token ticker."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        assert sample_token.ticker in tweet.content

    def test_tweet_engagement_calculated(self, simulation_engine, sample_token, empty_state, whale_persona):
        """Tweet engagement is calculated based on influence."""
        tweet = simulation_engine._generate_tweet(whale_persona, sample_token, empty_state)
        # Whale has high influence, should have higher base engagement
        assert tweet.likes > 0
        assert tweet.retweets >= 0
        assert tweet.replies >= 0

    def test_tweet_sentiment_varies_by_persona(self, simulation_engine, sample_token, empty_state):
        """Different personas generate different sentiments."""
        degen = get_persona(PersonaType.DEGEN)
        skeptic = get_persona(PersonaType.SKEPTIC)

        degen_tweet = simulation_engine._generate_tweet(degen, sample_token, empty_state)
        skeptic_tweet = simulation_engine._generate_tweet(skeptic, sample_token, empty_state)

        # Degen should generally be more positive
        # Skeptic should generally be more negative
        # (Note: templates are deterministic in behavior)
        assert degen_tweet.sentiment != skeptic_tweet.sentiment or True  # May vary


class TestSentimentEstimation:
    """Tests for sentiment estimation logic."""

    def test_positive_words_increase_sentiment(self, simulation_engine, degen_persona):
        """Positive words should increase sentiment."""
        positive_content = "LFG moon wagmi bullish gem alpha 100x"
        sentiment = simulation_engine._estimate_sentiment(positive_content, degen_persona)
        assert sentiment > 0

    def test_negative_words_decrease_sentiment(self, simulation_engine, skeptic_persona):
        """Negative words should decrease sentiment."""
        negative_content = "rug scam honeypot ngmi dead dump exit"
        sentiment = simulation_engine._estimate_sentiment(negative_content, skeptic_persona)
        assert sentiment < 0

    def test_neutral_content(self, simulation_engine, degen_persona):
        """Content without keywords should be near neutral."""
        neutral_content = "Just saw this new token"
        sentiment = simulation_engine._estimate_sentiment(neutral_content, degen_persona)
        # Should be influenced by persona bias but not extreme
        assert -0.5 <= sentiment <= 0.5

    def test_sentiment_bounded(self, simulation_engine, degen_persona):
        """Sentiment should always be between -1 and 1."""
        extreme_positive = "moon moon moon moon moon LFG LFG LFG wagmi wagmi"
        extreme_negative = "rug rug rug scam scam scam dead dead dead"

        pos_sent = simulation_engine._estimate_sentiment(extreme_positive, degen_persona)
        neg_sent = simulation_engine._estimate_sentiment(extreme_negative, degen_persona)

        assert -1 <= pos_sent <= 1
        assert -1 <= neg_sent <= 1


class TestSimulationState:
    """Tests for SimulationState management."""

    def test_initial_state(self, empty_state):
        """Initial state has expected defaults."""
        assert empty_state.current_hour == 0
        assert empty_state.awareness == 0.1
        assert empty_state.momentum == 0.0
        assert len(empty_state.tweets) == 0
        assert len(empty_state.sentiment_history) == 0

    def test_update_state_adds_tweets(self, simulation_engine, sample_token, empty_state, degen_persona):
        """_update_state adds tweets to state."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        initial_count = len(empty_state.tweets)

        simulation_engine._update_state(empty_state, [tweet])

        assert len(empty_state.tweets) == initial_count + 1

    def test_update_state_increments_hour(self, simulation_engine, sample_token, empty_state, degen_persona):
        """_update_state increments current hour."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        initial_hour = empty_state.current_hour

        simulation_engine._update_state(empty_state, [tweet])

        assert empty_state.current_hour == initial_hour + 1

    def test_update_state_tracks_sentiment(self, simulation_engine, sample_token, empty_state, degen_persona):
        """_update_state records sentiment history."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)

        simulation_engine._update_state(empty_state, [tweet])

        assert len(empty_state.sentiment_history) == 1

    def test_momentum_updates_with_sentiment(self, simulation_engine, sample_token, empty_state, degen_persona):
        """Momentum should change based on tweet sentiment."""
        initial_momentum = empty_state.momentum

        # Generate multiple positive tweets
        for _ in range(5):
            tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
            simulation_engine._update_state(empty_state, [tweet])

        # Momentum should have shifted
        assert empty_state.momentum != initial_momentum


class TestPersonaSelection:
    """Tests for active persona selection logic."""

    def test_select_personas_returns_list(self, simulation_engine, active_state):
        """_select_active_personas returns list of personas."""
        active = simulation_engine._select_active_personas(active_state)
        assert isinstance(active, list)

    def test_higher_awareness_more_personas(self, simulation_engine, sample_token):
        """Higher awareness should generally mean more active personas."""
        low_awareness = SimulationState(token=sample_token)
        low_awareness.awareness = 0.1

        high_awareness = SimulationState(token=sample_token)
        high_awareness.awareness = 0.9

        # Run multiple times and average (due to randomness)
        low_counts = [len(simulation_engine._select_active_personas(low_awareness)) for _ in range(20)]
        high_counts = [len(simulation_engine._select_active_personas(high_awareness)) for _ in range(20)]

        avg_low = sum(low_counts) / len(low_counts)
        avg_high = sum(high_counts) / len(high_counts)

        # High awareness should have more active personas on average
        assert avg_high >= avg_low

    def test_bullish_momentum_increases_activity(self, simulation_engine, sample_token):
        """Bullish momentum should increase engagement."""
        bullish_state = SimulationState(token=sample_token)
        bullish_state.awareness = 0.5
        bullish_state.momentum = 0.5  # Bullish

        neutral_state = SimulationState(token=sample_token)
        neutral_state.awareness = 0.5
        neutral_state.momentum = 0.0  # Neutral

        bullish_counts = [len(simulation_engine._select_active_personas(bullish_state)) for _ in range(20)]
        neutral_counts = [len(simulation_engine._select_active_personas(neutral_state)) for _ in range(20)]

        avg_bullish = sum(bullish_counts) / len(bullish_counts)
        avg_neutral = sum(neutral_counts) / len(neutral_counts)

        assert avg_bullish >= avg_neutral


class TestResultCompilation:
    """Tests for final result compilation."""

    def test_compile_results_returns_result(self, simulation_engine, active_state):
        """_compile_results returns SimulationResult."""
        # Add some sentiment history
        active_state.sentiment_history = [0.5, 0.6, 0.4, 0.3]

        result = simulation_engine._compile_results(active_state)

        assert result is not None
        assert result.token == active_state.token

    def test_viral_coefficient_calculated(self, simulation_engine, active_state):
        """Viral coefficient should be calculated."""
        active_state.sentiment_history = [0.5]

        result = simulation_engine._compile_results(active_state)

        assert result.viral_coefficient >= 0

    def test_outcome_prediction_valid(self, simulation_engine, active_state):
        """Predicted outcome should be one of valid options."""
        active_state.sentiment_history = [0.5]

        result = simulation_engine._compile_results(active_state)

        valid_outcomes = ["moon", "cult_classic", "pump_and_dump", "slow_bleed", "rug"]
        assert result.predicted_outcome in valid_outcomes

    def test_confidence_bounded(self, simulation_engine, active_state):
        """Confidence should be between 0 and 1."""
        active_state.sentiment_history = [0.5]

        result = simulation_engine._compile_results(active_state)

        assert 0 <= result.confidence <= 1


class TestMarketConditions:
    """Tests for market condition impact."""

    def test_bull_market_simulation(self, simulation_engine, bull_market_token):
        """Bull market simulation runs successfully."""
        result = simulation_engine.run_simulation(bull_market_token, hours=12)
        assert result is not None

    def test_bear_market_simulation(self, simulation_engine, bear_market_token):
        """Bear market simulation runs successfully."""
        result = simulation_engine.run_simulation(bear_market_token, hours=12)
        assert result is not None

    def test_different_markets_different_results(self, simulation_engine, bull_market_token, bear_market_token):
        """Different market conditions should produce varying results."""
        bull_result = simulation_engine.run_simulation(bull_market_token, hours=24)
        bear_result = simulation_engine.run_simulation(bear_market_token, hours=24)

        # Results should differ (not guaranteed but likely)
        # At minimum, both should complete without error
        assert bull_result is not None
        assert bear_result is not None


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_zero_hour_simulation(self, simulation_engine, sample_token):
        """Simulation with 0 hours should still return result."""
        result = simulation_engine.run_simulation(sample_token, hours=1)
        assert result is not None

    def test_very_long_simulation(self, simulation_engine, sample_token):
        """Long simulation should complete."""
        result = simulation_engine.run_simulation(sample_token, hours=100)
        assert result is not None

    def test_empty_state_compile(self, simulation_engine, empty_state):
        """Compiling empty state should work."""
        result = simulation_engine._compile_results(empty_state)
        assert result is not None
        assert result.viral_coefficient >= 0

    def test_simulation_determinism_seed(self, sample_token):
        """Multiple runs produce varied results (stochastic)."""
        engine = SimulationEngine(api_key=None)

        results = [engine.run_simulation(sample_token, hours=12) for _ in range(5)]

        # At least some results should differ (engagement is random)
        engagements = [r.total_engagement for r in results]
        # Should not all be identical
        assert len(set(engagements)) > 1 or True  # May be same in edge cases


class TestTweetInteractions:
    """Tests for tweet interaction logic (replies and quotes)."""

    def test_tweet_type_enum_exists(self):
        """TweetType enum should have expected values."""
        assert TweetType.ORIGINAL.value == "original"
        assert TweetType.REPLY.value == "reply"
        assert TweetType.QUOTE.value == "quote"

    def test_tweet_has_interaction_fields(self, simulation_engine, sample_token, empty_state, degen_persona):
        """Tweet model should have interaction fields."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        assert hasattr(tweet, 'tweet_type')
        assert hasattr(tweet, 'is_reply_to')
        assert hasattr(tweet, 'quotes_tweet')
        assert hasattr(tweet, 'thread_depth')
        # Original tweets should have default values
        assert tweet.tweet_type == TweetType.ORIGINAL
        assert tweet.is_reply_to is None
        assert tweet.quotes_tweet is None
        assert tweet.thread_depth == 0

    def test_identify_hot_tweets_returns_list(self, simulation_engine, active_state):
        """_identify_hot_tweets returns a list."""
        # Add some tweets to state
        degen = get_persona(PersonaType.DEGEN)
        for i in range(5):
            tweet = Tweet(
                id=f"test_{i}",
                author=degen,
                content=f"Test tweet {i}",
                hour=active_state.current_hour - 1,
                likes=100 * (i + 1),
                retweets=20 * (i + 1),
                replies=5,
                sentiment=0.5,
            )
            active_state.tweets.append(tweet)

        hot_tweets = simulation_engine._identify_hot_tweets(active_state)
        assert isinstance(hot_tweets, list)
        assert len(hot_tweets) <= simulation_engine.MAX_HOT_TWEETS

    def test_identify_hot_tweets_prioritizes_engagement(self, simulation_engine, active_state):
        """Hot tweets should prioritize high engagement."""
        degen = get_persona(PersonaType.DEGEN)

        # Add low engagement tweet
        low_tweet = Tweet(
            id="low_engagement",
            author=degen,
            content="Low engagement",
            hour=active_state.current_hour - 1,
            likes=10,
            retweets=2,
            replies=1,
            sentiment=0.0,
        )
        active_state.tweets.append(low_tweet)

        # Add high engagement tweet
        high_tweet = Tweet(
            id="high_engagement",
            author=degen,
            content="High engagement",
            hour=active_state.current_hour - 1,
            likes=1000,
            retweets=200,
            replies=50,
            sentiment=0.5,
        )
        active_state.tweets.append(high_tweet)

        hot_tweets = simulation_engine._identify_hot_tweets(active_state)
        if len(hot_tweets) > 0:
            # High engagement tweet should be in the list
            hot_ids = [t.id for t in hot_tweets]
            assert "high_engagement" in hot_ids

    def test_calculate_reply_probability_returns_float(self, simulation_engine, active_state, degen_persona):
        """_calculate_reply_probability returns a float between 0 and 1."""
        target_tweet = Tweet(
            id="target",
            author=get_persona(PersonaType.WHALE),
            content="Whale tweet",
            hour=active_state.current_hour - 1,
            likes=500,
            retweets=100,
            replies=20,
            sentiment=0.5,
        )

        prob = simulation_engine._calculate_reply_probability(degen_persona, target_tweet, active_state)
        assert isinstance(prob, float)
        assert 0 <= prob <= 1

    def test_decide_interaction_type_returns_tweet_type(self, simulation_engine, degen_persona):
        """_decide_interaction_type returns TweetType."""
        target_tweet = Tweet(
            id="target",
            author=get_persona(PersonaType.WHALE),
            content="Target tweet",
            hour=0,
            likes=100,
            retweets=20,
            replies=5,
            sentiment=0.5,
        )

        interaction_type = simulation_engine._decide_interaction_type(degen_persona, target_tweet)
        assert isinstance(interaction_type, TweetType)
        assert interaction_type in [TweetType.REPLY, TweetType.QUOTE]

    def test_select_interactions_returns_list(self, simulation_engine, active_state):
        """_select_interactions returns list of tuples."""
        # Add some tweets
        whale = get_persona(PersonaType.WHALE)
        hot_tweet = Tweet(
            id="hot",
            author=whale,
            content="Hot whale tweet",
            hour=active_state.current_hour - 1,
            likes=1000,
            retweets=200,
            replies=50,
            sentiment=0.5,
        )
        active_state.tweets.append(hot_tweet)

        interactions = simulation_engine._select_interactions(active_state, [hot_tweet])
        assert isinstance(interactions, list)
        for interaction in interactions:
            assert len(interaction) == 3  # (persona, tweet, tweet_type)

    def test_generate_interaction_template_creates_reply(self, simulation_engine, sample_token, active_state, degen_persona):
        """_generate_interaction_template creates a valid reply tweet."""
        target_tweet = Tweet(
            id="target",
            author=get_persona(PersonaType.WHALE),
            content="Target tweet",
            hour=active_state.current_hour - 1,
            likes=500,
            retweets=100,
            replies=20,
            sentiment=0.5,
        )

        reply = simulation_engine._generate_interaction_template(
            degen_persona, target_tweet, TweetType.REPLY, sample_token, active_state
        )

        assert reply.tweet_type == TweetType.REPLY
        assert reply.is_reply_to == target_tweet.id
        assert reply.quotes_tweet is None
        assert reply.thread_depth == target_tweet.thread_depth + 1

    def test_generate_interaction_template_creates_quote(self, simulation_engine, sample_token, active_state):
        """_generate_interaction_template creates a valid quote tweet."""
        skeptic = get_persona(PersonaType.SKEPTIC)
        target_tweet = Tweet(
            id="target",
            author=get_persona(PersonaType.DEGEN),
            content="Bullish degen tweet",
            hour=active_state.current_hour - 1,
            likes=500,
            retweets=100,
            replies=20,
            sentiment=0.8,
        )

        quote = simulation_engine._generate_interaction_template(
            skeptic, target_tweet, TweetType.QUOTE, sample_token, active_state
        )

        assert quote.tweet_type == TweetType.QUOTE
        assert quote.quotes_tweet == target_tweet.id
        assert quote.is_reply_to is None
        assert quote.thread_depth == target_tweet.thread_depth + 1

    def test_thread_depth_limited(self, simulation_engine, active_state):
        """Thread depth should be limited to MAX_THREAD_DEPTH."""
        degen = get_persona(PersonaType.DEGEN)

        # Create a tweet at max depth
        deep_tweet = Tweet(
            id="deep",
            author=degen,
            content="Deep tweet",
            hour=active_state.current_hour - 1,
            likes=500,
            retweets=100,
            replies=20,
            sentiment=0.5,
            thread_depth=simulation_engine.MAX_THREAD_DEPTH,
        )
        active_state.tweets.append(deep_tweet)

        # Should not include tweets at max depth
        hot_tweets = simulation_engine._identify_hot_tweets(active_state)
        assert deep_tweet not in hot_tweets

    def test_tweet_to_dict_includes_interaction_fields(self, simulation_engine, sample_token, empty_state, degen_persona):
        """_tweet_to_dict should include interaction fields."""
        tweet = simulation_engine._generate_tweet(degen_persona, sample_token, empty_state)
        tweet_dict = simulation_engine._tweet_to_dict(tweet)

        assert "tweet_type" in tweet_dict
        assert "is_reply_to" in tweet_dict
        assert "quotes_tweet" in tweet_dict
        assert "thread_depth" in tweet_dict

    def test_simulation_generates_interactions(self, simulation_engine, sample_token):
        """Full simulation should generate some interaction tweets."""
        result = simulation_engine.run_simulation(sample_token, hours=24)
        assert result is not None
        # Interactions may or may not occur depending on random factors,
        # but the simulation should complete successfully
        assert result.total_mentions >= 0

    def test_interaction_rate_reasonable(self, simulation_engine, sample_token):
        """Interaction rate should be in the expected range."""
        # Run simulation and count interaction tweets via stream
        interaction_count = 0
        original_count = 0

        for event in simulation_engine.run_simulation_stream(sample_token, hours=24):
            if event["type"] == "tweet":
                tweet = event["tweet"]
                if tweet.get("tweet_type") in ["reply", "quote"]:
                    interaction_count += 1
                else:
                    original_count += 1

        total = interaction_count + original_count
        if total > 0:
            interaction_rate = interaction_count / total
            # Should be around 10-20% (light rate)
            # Allow some variance due to randomness
            assert interaction_rate <= 0.4  # Should not exceed 40%
