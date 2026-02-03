"""Multi-token competition simulator.

Simulates multiple tokens competing for attention on CT simultaneously.
"""

import os
import random
import logging
from typing import Optional
import anthropic

from ..models.token import Token, SimulationResult
from .engine import SimulationEngine, SimulationState

logger = logging.getLogger(__name__)


class CompetitionSimulator:
    """Simulates multiple tokens competing on CT."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def run_competition(
        self,
        tokens: list[Token],
        hours: int = 48,
    ) -> list[SimulationResult]:
        """
        Run a competition simulation for multiple tokens.

        Each token gets its own simulation, but they share market dynamics:
        - Attention is split between tokens
        - Strong tokens can steal momentum from weaker ones
        - Market sentiment affects all tokens

        Args:
            tokens: List of tokens competing
            hours: Duration of simulation

        Returns:
            List of SimulationResult for each token (same order as input)
        """
        # Create single shared engine and state for each token
        engine = SimulationEngine(api_key=self.api_key)
        states = [SimulationState(token=token) for token in tokens]

        # Competition dynamics: attention is split
        attention_split = 1.0 / len(tokens)

        # Initial bot alerts for all tokens
        from ..agents.personas import get_persona, PersonaType
        bot = get_persona(PersonaType.BOT)

        for i, state in enumerate(states):
            initial_tweet = engine._generate_tweet(bot, tokens[i], state)
            engine._update_state(state, [initial_tweet])

        # Run simulation hour by hour with competition dynamics
        for hour in range(1, hours):
            # Calculate relative momentum (who's winning attention)
            total_momentum = sum(max(0.1, s.momentum + 0.5) for s in states)
            attention_shares = [
                max(0.1, s.momentum + 0.5) / total_momentum for s in states
            ]

            # Update each token's simulation
            for i, (state, token) in enumerate(zip(states, tokens)):
                # Attention modifier based on competition
                attention_modifier = attention_shares[i] / attention_split

                # Select personas (fewer if losing attention battle)
                active_personas = engine._select_active_personas(state)
                if attention_modifier < 0.8:
                    # Losing attention - fewer people engage
                    cutoff = int(len(active_personas) * attention_modifier)
                    active_personas = active_personas[:max(1, cutoff)]

                # Get recent context
                recent_tweets = state.tweets[-5:] if state.tweets else []
                context = "\n".join(f"@{t.author.handle}: {t.content}" for t in recent_tweets)

                # Generate tweets
                new_tweets = engine._generate_tweets_batch(active_personas, token, state, context)

                # Generate interactions
                hot_tweets = engine._identify_hot_tweets(state)
                interactions = engine._select_interactions(state, hot_tweets)
                interaction_tweets = engine._generate_interactions_batch(interactions, token, state)
                new_tweets.extend(interaction_tweets)

                # Apply competition effects to momentum
                # Winners get momentum boost, losers get penalized
                if attention_modifier > 1.2:
                    # Winning - momentum boost
                    for tweet in new_tweets:
                        tweet.likes = int(tweet.likes * 1.2)
                        tweet.retweets = int(tweet.retweets * 1.2)
                elif attention_modifier < 0.8:
                    # Losing - momentum penalty
                    for tweet in new_tweets:
                        tweet.likes = int(tweet.likes * 0.8)
                        tweet.retweets = int(tweet.retweets * 0.8)

                engine._update_state(state, new_tweets)

            # Cross-token effects: skeptics might compare tokens
            self._apply_cross_token_effects(states, hour)

        # Compile results for all tokens
        results = []
        for state in states:
            result = engine._compile_results(state)
            results.append(result)

        return results

    def _apply_cross_token_effects(
        self,
        states: list[SimulationState],
        hour: int
    ) -> None:
        """Apply cross-token competition effects.

        When one token is clearly winning, it can affect others' momentum.
        """
        if hour % 4 != 0:  # Only check every 4 hours
            return

        momentums = [s.momentum for s in states]
        max_momentum = max(momentums)
        min_momentum = min(momentums)

        # If there's a clear leader, boost their momentum slightly
        # and slightly penalize laggards
        if max_momentum - min_momentum > 0.3:
            for state in states:
                if state.momentum == max_momentum:
                    state.momentum = min(1.0, state.momentum + 0.05)
                elif state.momentum == min_momentum:
                    state.momentum = max(-1.0, state.momentum - 0.05)

    def analyze_competition(
        self,
        tokens: list[Token],
        results: list[SimulationResult]
    ) -> str:
        """Generate LLM analysis of the competition results."""

        if not self.client:
            # Fallback analysis without LLM
            sorted_results = sorted(
                zip(tokens, results),
                key=lambda x: x[1].viral_coefficient,
                reverse=True
            )
            winner = sorted_results[0][0]
            return f"${winner.ticker} dominated the competition with superior viral coefficient and engagement."

        # Build context for LLM analysis
        token_summaries = []
        for token, result in sorted(
            zip(tokens, results),
            key=lambda x: x[1].viral_coefficient,
            reverse=True
        ):
            token_summaries.append(f"""${token.ticker} ({token.name}):
- Narrative: {token.narrative}
- Viral Coefficient: {result.viral_coefficient:.2f}x
- Peak Sentiment: {result.peak_sentiment:.2f}
- Total Engagement: {result.total_engagement:,}
- Influencer Pickups: {result.influencer_pickups}
- Predicted Outcome: {result.predicted_outcome}""")

        prompt = f"""Analyze this crypto token competition simulation on CT.

{chr(10).join(token_summaries)}

Provide a brief (2-3 sentences) analysis of:
1. Why the winner performed better
2. What the losers could have done differently
3. Any interesting dynamics between the tokens

Be direct and analytical. Use CT language where appropriate."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.warning(f"Competition analysis failed: {e}")
            sorted_results = sorted(
                zip(tokens, results),
                key=lambda x: x[1].viral_coefficient,
                reverse=True
            )
            winner = sorted_results[0][0]
            return f"${winner.ticker} dominated the competition with superior viral coefficient and engagement."
