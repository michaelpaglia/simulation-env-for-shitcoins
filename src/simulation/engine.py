"""Core simulation engine - runs the shitcoin social simulation."""

import random
from typing import Optional
from pydantic import BaseModel, Field
import anthropic

from ..models.token import Token, SimulationResult, MarketCondition
from ..agents.personas import Persona, PersonaType, get_all_personas, get_persona


class Tweet(BaseModel):
    """A simulated tweet."""

    id: str
    author: Persona
    content: str
    hour: int  # Simulation hour

    likes: int = 0
    retweets: int = 0
    replies: int = 0

    sentiment: float = Field(default=0, ge=-1, le=1)  # -1 FUD to 1 hype
    is_reply_to: Optional[str] = None


class SimulationState(BaseModel):
    """Current state of a simulation run."""

    token: Token
    current_hour: int = 0

    tweets: list[Tweet] = Field(default_factory=list)
    sentiment_history: list[float] = Field(default_factory=list)

    # Aggregate metrics
    total_mentions: int = 0
    total_engagement: int = 0
    influencer_mentions: int = 0

    # Viral tracking
    awareness: float = 0.1  # What % of CT knows about this token
    momentum: float = 0.0   # Current viral momentum (-1 to 1)


class SimulationEngine:
    """Runs shitcoin social simulations."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.personas = get_all_personas()

    def _generate_tweet(
        self,
        persona: Persona,
        token: Token,
        state: SimulationState,
        context: Optional[str] = None
    ) -> Tweet:
        """Generate a tweet from a persona about the token."""

        if self.client:
            # Use Claude for realistic generation
            system_prompt = persona.get_system_prompt()

            user_prompt = f"""New token just dropped:

{token.get_pitch()}

Market condition: {token.market_condition.value}
Current CT sentiment: {"bullish" if state.momentum > 0.3 else "bearish" if state.momentum < -0.3 else "neutral"}
Awareness level: {state.awareness:.0%} of CT knows about it

{f"Context from other tweets: {context}" if context else ""}

React to this token. Stay in character. One tweet only."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )
            content = response.content[0].text.strip()

            # Estimate sentiment from content
            sentiment = self._estimate_sentiment(content, persona)
        else:
            # Fallback: template-based generation
            content, sentiment = self._generate_template_tweet(persona, token, state)

        # Calculate engagement based on persona influence and momentum
        base_engagement = int(persona.influence_score * 1000)
        momentum_multiplier = 1 + (state.momentum * 0.5)

        tweet = Tweet(
            id=f"tweet_{state.current_hour}_{persona.handle}",
            author=persona,
            content=content,
            hour=state.current_hour,
            likes=int(base_engagement * momentum_multiplier * random.uniform(0.5, 1.5)),
            retweets=int(base_engagement * 0.3 * momentum_multiplier * random.uniform(0.3, 1.2)),
            replies=int(base_engagement * 0.1 * random.uniform(0.5, 2.0)),
            sentiment=sentiment,
        )

        return tweet

    def _estimate_sentiment(self, content: str, persona: Persona) -> float:
        """Estimate sentiment of tweet content."""
        content_lower = content.lower()

        # Positive signals
        positive = ["moon", "lfg", "wagmi", "bullish", "gem", "early", "based", "100x", "alpha"]
        # Negative signals
        negative = ["rug", "scam", "honeypot", "ngmi", "dead", "dump", "sell", "exit"]

        pos_count = sum(1 for word in positive if word in content_lower)
        neg_count = sum(1 for word in negative if word in content_lower)

        # Adjust by persona tendency
        base_sentiment = (pos_count - neg_count) / max(pos_count + neg_count, 1)
        persona_bias = persona.fomo_susceptibility - persona.fud_generation

        return max(-1, min(1, (base_sentiment + persona_bias) / 2))

    def _generate_template_tweet(
        self,
        persona: Persona,
        token: Token,
        state: SimulationState
    ) -> tuple[str, float]:
        """Generate a tweet using templates (no LLM fallback)."""

        templates = {
            PersonaType.DEGEN: [
                (f"${token.ticker} looks interesting, aped a smol bag LFG 🚀", 0.7),
                (f"ser this ${token.ticker} chart is doing things to me", 0.5),
                (f"${token.ticker}??? say less, I'm in", 0.8),
            ],
            PersonaType.SKEPTIC: [
                (f"${token.ticker} - anon team, no audit, unlocked LP. Classic rug setup.", -0.8),
                (f"Why would anyone buy ${token.ticker}? Genuine question.", -0.5),
                (f"${token.ticker} holders are exit liquidity. DYOR.", -0.7),
            ],
            PersonaType.WHALE: [
                (f"${token.ticker}", 0.3),
                ("interesting", 0.4),
                ("watching.", 0.2),
            ],
            PersonaType.INFLUENCER: [
                (f"Just found ${token.ticker} - this could be big. Early alpha for my followers 👀", 0.8),
                (f"${token.ticker} thread coming soon. You're not ready.", 0.6),
                (f"CT is sleeping on ${token.ticker}. Don't say I didn't warn you.", 0.7),
            ],
            PersonaType.NORMIE: [
                (f"Is ${token.ticker} legit? Should I buy?", 0.2),
                (f"Just bought some ${token.ticker}, hope this moons!", 0.5),
                (f"What's the deal with ${token.ticker}?", 0.0),
            ],
            PersonaType.BOT: [
                (f"🚨 NEW TOKEN: ${token.ticker}\nHolders: {random.randint(50, 500)}\nVol: ${random.randint(10, 100)}K", 0.0),
            ],
        }

        options = templates.get(persona.type, [(f"${token.ticker}", 0.0)])
        return random.choice(options)

    def _update_state(self, state: SimulationState, new_tweets: list[Tweet]) -> None:
        """Update simulation state after a round of tweets."""

        state.tweets.extend(new_tweets)

        # Calculate average sentiment this hour
        if new_tweets:
            hour_sentiment = sum(t.sentiment for t in new_tweets) / len(new_tweets)
            state.sentiment_history.append(hour_sentiment)

            # Update momentum (momentum is sticky)
            state.momentum = state.momentum * 0.7 + hour_sentiment * 0.3

            # Update awareness based on engagement and influencer activity
            total_engagement = sum(t.likes + t.retweets + t.replies for t in new_tweets)
            influencer_boost = sum(
                0.05 for t in new_tweets
                if t.author.type in [PersonaType.WHALE, PersonaType.INFLUENCER]
            )

            state.awareness = min(1.0, state.awareness + (total_engagement / 50000) + influencer_boost)

            # Update counters
            state.total_mentions += len(new_tweets)
            state.total_engagement += total_engagement
            state.influencer_mentions += sum(
                1 for t in new_tweets
                if t.author.type in [PersonaType.WHALE, PersonaType.INFLUENCER]
            )

        state.current_hour += 1

    def _select_active_personas(self, state: SimulationState) -> list[Persona]:
        """Select which personas tweet this hour based on engagement rates and awareness."""

        active = []
        market = state.token.market_condition

        for persona in self.personas:
            # Higher awareness = more people talking
            adjusted_rate = persona.engagement_rate * state.awareness

            # Market condition affects persona behavior
            if market == MarketCondition.BEAR:
                if persona.type == PersonaType.SKEPTIC:
                    adjusted_rate *= 2.0  # Skeptics dominate in bear
                elif persona.type == PersonaType.DEGEN:
                    adjusted_rate *= 0.5  # Degens retreat
                elif persona.type == PersonaType.INFLUENCER:
                    adjusted_rate *= 0.6  # Influencers less active
                else:
                    adjusted_rate *= 0.7
            elif market == MarketCondition.EUPHORIA:
                if persona.type == PersonaType.DEGEN:
                    adjusted_rate *= 2.0  # Degens go wild
                elif persona.type == PersonaType.SKEPTIC:
                    adjusted_rate *= 0.4  # Skeptics drowned out
                else:
                    adjusted_rate *= 1.5
            elif market == MarketCondition.BULL:
                if persona.type == PersonaType.DEGEN:
                    adjusted_rate *= 1.5
                elif persona.type == PersonaType.SKEPTIC:
                    adjusted_rate *= 0.7

            # Momentum also affects engagement
            if state.momentum > 0.3:  # Bullish momentum
                adjusted_rate *= 1.3
            elif state.momentum < -0.3:  # Bearish momentum
                if persona.type == PersonaType.SKEPTIC:
                    adjusted_rate *= 1.5  # Skeptics pile on
                else:
                    adjusted_rate *= 0.7  # Others disengage

            if random.random() < adjusted_rate:
                active.append(persona)

        return active

    def run_simulation(
        self,
        token: Token,
        hours: int = 48,
        verbose: bool = False
    ) -> SimulationResult:
        """Run a full simulation for a token."""

        state = SimulationState(token=token)

        # Initial seeding - bot alerts first
        bot = get_persona(PersonaType.BOT)
        initial_tweet = self._generate_tweet(bot, token, state)
        self._update_state(state, [initial_tweet])

        # Run simulation
        for hour in range(1, hours):
            active_personas = self._select_active_personas(state)

            if verbose:
                print(f"Hour {hour}: {len(active_personas)} active users, "
                      f"momentum={state.momentum:.2f}, awareness={state.awareness:.0%}")

            # Get recent context for LLM
            recent_tweets = state.tweets[-5:] if state.tweets else []
            context = "\n".join(f"@{t.author.handle}: {t.content}" for t in recent_tweets)

            # Generate tweets
            new_tweets = [
                self._generate_tweet(persona, token, state, context)
                for persona in active_personas
            ]

            self._update_state(state, new_tweets)

            # Check for death (momentum crashed and awareness is low)
            if state.momentum < -0.7 and state.awareness < 0.3 and hour > 12:
                if verbose:
                    print(f"Token died at hour {hour}")
                break

        # Calculate final results
        return self._compile_results(state)

    def run_simulation_stream(
        self,
        token: Token,
        hours: int = 48,
    ):
        """
        Generator that yields simulation events as they occur.

        Yields dicts with type: 'tweet', 'progress', or 'result'
        """
        state = SimulationState(token=token)

        # Initial seeding - bot alerts first
        bot = get_persona(PersonaType.BOT)
        initial_tweet = self._generate_tweet(bot, token, state)
        self._update_state(state, [initial_tweet])

        # Yield initial tweet
        yield {
            "type": "tweet",
            "tweet": self._tweet_to_dict(initial_tweet),
        }

        yield {
            "type": "progress",
            "hour": 0,
            "total_hours": hours,
            "momentum": state.momentum,
            "awareness": state.awareness,
            "tweet_count": len(state.tweets),
        }

        # Run simulation
        for hour in range(1, hours):
            active_personas = self._select_active_personas(state)

            # Get recent context for LLM
            recent_tweets = state.tweets[-5:] if state.tweets else []
            context = "\n".join(f"@{t.author.handle}: {t.content}" for t in recent_tweets)

            # Generate and yield tweets one by one
            new_tweets = []
            for persona in active_personas:
                tweet = self._generate_tweet(persona, token, state, context)
                new_tweets.append(tweet)

                # Yield each tweet immediately
                yield {
                    "type": "tweet",
                    "tweet": self._tweet_to_dict(tweet),
                }

            self._update_state(state, new_tweets)

            # Yield progress update
            yield {
                "type": "progress",
                "hour": hour,
                "total_hours": hours,
                "momentum": round(state.momentum, 3),
                "awareness": round(state.awareness, 3),
                "tweet_count": len(state.tweets),
            }

            # Check for death
            if state.momentum < -0.7 and state.awareness < 0.3 and hour > 12:
                yield {
                    "type": "status",
                    "message": f"Token died at hour {hour}",
                }
                break

        # Yield final results
        result = self._compile_results(state)
        yield {
            "type": "result",
            "result": {
                "viral_coefficient": result.viral_coefficient,
                "peak_sentiment": result.peak_sentiment,
                "sentiment_stability": result.sentiment_stability,
                "fud_resistance": result.fud_resistance,
                "total_mentions": result.total_mentions,
                "total_engagement": result.total_engagement,
                "influencer_pickups": result.influencer_pickups,
                "hours_to_peak": result.hours_to_peak,
                "hours_to_death": result.hours_to_death,
                "dominant_narrative": result.dominant_narrative,
                "top_fud_points": result.top_fud_points,
                "predicted_outcome": result.predicted_outcome,
                "confidence": result.confidence,
            }
        }

    def _tweet_to_dict(self, tweet: Tweet) -> dict:
        """Convert a Tweet to a serializable dict."""
        return {
            "id": tweet.id,
            "author_name": tweet.author.name,
            "author_handle": tweet.author.handle,
            "author_type": tweet.author.type.value,
            "content": tweet.content,
            "hour": tweet.hour,
            "likes": tweet.likes,
            "retweets": tweet.retweets,
            "replies": tweet.replies,
            "sentiment": tweet.sentiment,
        }

    def _compile_results(self, state: SimulationState) -> SimulationResult:
        """Compile final simulation results."""

        # Viral coefficient (rough: engagement per mention / baseline)
        viral_coef = (state.total_engagement / max(state.total_mentions, 1)) / 100

        # Peak sentiment
        peak_sentiment = max(state.sentiment_history) if state.sentiment_history else 0

        # Stability (inverse of variance)
        if len(state.sentiment_history) > 1:
            mean_sent = sum(state.sentiment_history) / len(state.sentiment_history)
            variance = sum((s - mean_sent) ** 2 for s in state.sentiment_history) / len(state.sentiment_history)
            stability = max(0, 1 - variance)
        else:
            stability = 0.5

        # FUD resistance
        skeptic_tweets = [t for t in state.tweets if t.author.type == PersonaType.SKEPTIC]
        if skeptic_tweets:
            fud_impact = sum(t.sentiment for t in skeptic_tweets) / len(skeptic_tweets)
            fud_resistance = max(0, min(1, 0.5 - fud_impact))
        else:
            fud_resistance = 0.7

        # Find peak hour
        hours_to_peak = state.sentiment_history.index(peak_sentiment) if state.sentiment_history else 0

        # Determine if/when it died
        hours_to_death = None
        if state.momentum < -0.5:
            hours_to_death = state.current_hour

        # Determine dominant narrative
        all_content = " ".join(t.content for t in state.tweets[-10:])
        if "rug" in all_content.lower() or "scam" in all_content.lower():
            dominant_narrative = "Another rug in the making"
        elif "gem" in all_content.lower() or "early" in all_content.lower():
            dominant_narrative = "Hidden gem - early opportunity"
        elif "interesting" in all_content.lower():
            dominant_narrative = "Worth watching"
        else:
            dominant_narrative = f"Generic {state.token.meme_style.value} play"

        # Extract FUD points
        fud_tweets = [t.content for t in state.tweets if t.sentiment < -0.3]
        top_fud = fud_tweets[:3] if fud_tweets else ["No significant FUD detected"]

        # Predict outcome - market conditions affect thresholds
        market = state.token.market_condition

        # Market-adjusted thresholds
        if market == MarketCondition.BEAR:
            moon_viral_threshold = 3.0  # Harder to moon in bear
            moon_sentiment_threshold = 0.7
            cult_viral_threshold = 1.5
            death_momentum_threshold = -0.3  # Easier to die
            # Add randomness - bear markets are unpredictable
            random_factor = random.uniform(-0.2, 0.1)
        elif market == MarketCondition.EUPHORIA:
            moon_viral_threshold = 1.0  # Easy to moon
            moon_sentiment_threshold = 0.3
            cult_viral_threshold = 0.5
            death_momentum_threshold = -0.8  # Hard to kill
            random_factor = random.uniform(-0.1, 0.2)
        else:  # CRAB or BULL
            moon_viral_threshold = 2.0
            moon_sentiment_threshold = 0.6
            cult_viral_threshold = 1.0
            death_momentum_threshold = -0.5
            random_factor = random.uniform(-0.1, 0.1)

        # Adjust momentum with random factor for outcome calculation
        adjusted_momentum = state.momentum + random_factor

        # Predict outcome
        if viral_coef > moon_viral_threshold and peak_sentiment > moon_sentiment_threshold and fud_resistance > 0.6:
            outcome = "moon"
            confidence = min(0.8, viral_coef / 5)
        elif viral_coef > cult_viral_threshold and adjusted_momentum > 0:
            outcome = "cult_classic"
            confidence = 0.5
        elif adjusted_momentum < death_momentum_threshold:
            outcome = "rug" if fud_resistance < 0.5 else "slow_bleed"
            confidence = 0.6
        elif fud_resistance < 0.4 or (market == MarketCondition.BEAR and random.random() < 0.3):
            # In bear markets, there's a chance of slow bleed even without crashed momentum
            outcome = "slow_bleed" if random.random() < 0.7 else "rug"
            confidence = 0.5
        else:
            outcome = "pump_and_dump"
            confidence = 0.4

        return SimulationResult(
            token=state.token,
            viral_coefficient=viral_coef,
            peak_sentiment=peak_sentiment,
            sentiment_stability=stability,
            fud_resistance=fud_resistance,
            total_mentions=state.total_mentions,
            total_engagement=state.total_engagement,
            influencer_pickups=state.influencer_mentions,
            hours_to_peak=hours_to_peak,
            hours_to_death=hours_to_death,
            dominant_narrative=dominant_narrative,
            top_fud_points=top_fud,
            predicted_outcome=outcome,
            confidence=confidence,
        )
