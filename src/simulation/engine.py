"""Core simulation engine - runs the shitcoin social simulation."""

import random
import json
import re
import logging
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import anthropic

logger = logging.getLogger(__name__)

from ..models.token import Token, SimulationResult, MarketCondition
from ..agents.personas import Persona, PersonaType, get_all_personas, get_persona

# Use Haiku for speed and cost efficiency
DEFAULT_MODEL = "claude-3-5-haiku-20241022"


class TweetType(str, Enum):
    """Type of tweet interaction."""
    ORIGINAL = "original"
    REPLY = "reply"
    QUOTE = "quote"


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

    # Interaction fields
    tweet_type: TweetType = TweetType.ORIGINAL
    is_reply_to: Optional[str] = None  # ID of parent tweet if reply
    quotes_tweet: Optional[str] = None  # ID of quoted tweet if quote
    thread_depth: int = 0  # Depth in conversation (0 = root, max 3)


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

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.model = model
        self.personas = get_all_personas()

    def _generate_tweets_batch(
        self,
        personas: list[Persona],
        token: Token,
        state: SimulationState,
        context: Optional[str] = None
    ) -> list[Tweet]:
        """Generate tweets for multiple personas in a single API call (much faster)."""

        if not personas:
            return []

        if not self.client:
            # Fallback to templates
            return [self._generate_tweet_template(p, token, state) for p in personas]

        # Build persona descriptions for batch generation
        persona_list = "\n".join([
            f"- @{p.handle} ({p.type.value}): {p.name}"
            for p in personas
        ])

        system_prompt = """You are simulating Crypto Twitter reactions to a new token.
Generate realistic tweets from multiple personas. Each persona has a distinct voice:
- degen: Apes everything, uses emojis, says "ser", "lfg", "wagmi"
- skeptic: Calls out red flags, warns about rugs, uses "ngmi", "dyor"
- whale: Minimal words, cryptic, high influence
- influencer: Hypes for clout, uses threads, builds narrative
- normie: Asks questions, unsure, follows crowd
- kol: Key opinion leader, analytical but can shill
- bot: Automated alerts, stats only

Keep tweets short (under 200 chars). Be authentic to CT culture."""

        user_prompt = f"""Token: ${token.ticker} - {token.name}
Narrative: {token.narrative}
Market: {token.market_condition.value}
CT mood: {"bullish" if state.momentum > 0.3 else "bearish" if state.momentum < -0.3 else "neutral"}
Awareness: {state.awareness:.0%}

{f"Recent tweets: {context}" if context else ""}

Generate ONE tweet for each of these personas:
{persona_list}

Return as JSON array:
[{{"handle": "@handle", "tweet": "tweet text", "sentiment": 0.5}}]
sentiment: -1 (FUD) to 1 (hype)"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=1.2,  # Higher temp for more varied CT-style tweets
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text

            # Parse JSON array from response using regex for robustness
            match = re.search(r'\[[\s\S]*\]', raw)
            if match:
                tweets_data = json.loads(match.group())
            else:
                logger.warning("No JSON array found in LLM response, using templates")
                tweets_data = []

            # Map responses back to personas
            handle_to_data = {t.get("handle", "").lstrip("@"): t for t in tweets_data}

            tweets = []
            for persona in personas:
                data = handle_to_data.get(persona.handle, {})
                content = data.get("tweet", "")
                sentiment = float(data.get("sentiment", 0))

                if not content:
                    # Fallback to template if no content
                    tweet = self._generate_tweet_template(persona, token, state)
                else:
                    tweet = self._create_tweet(persona, content, sentiment, state)

                tweets.append(tweet)

            return tweets

        except Exception as e:
            logger.warning(f"LLM tweet generation failed, using templates: {e}")
            return [self._generate_tweet_template(p, token, state) for p in personas]

    def _generate_tweet_template(
        self,
        persona: Persona,
        token: Token,
        state: SimulationState
    ) -> Tweet:
        """Generate a tweet using templates (fast fallback)."""
        content, sentiment = self._generate_template_tweet(persona, token, state)
        return self._create_tweet(persona, content, sentiment, state)

    def _create_tweet(
        self,
        persona: Persona,
        content: str,
        sentiment: float,
        state: SimulationState
    ) -> Tweet:
        """Create a Tweet object with calculated engagement."""
        base_engagement = int(persona.influence_score * 1000)
        momentum_multiplier = 1 + (state.momentum * 0.5)

        return Tweet(
            id=f"tweet_{state.current_hour}_{persona.handle}",
            author=persona,
            content=content,
            hour=state.current_hour,
            likes=int(base_engagement * momentum_multiplier * random.uniform(0.5, 1.5)),
            retweets=int(base_engagement * 0.3 * momentum_multiplier * random.uniform(0.3, 1.2)),
            replies=int(base_engagement * 0.1 * random.uniform(0.5, 2.0)),
            sentiment=max(-1, min(1, sentiment)),
        )

    def _generate_tweet(
        self,
        persona: Persona,
        token: Token,
        state: SimulationState,
        _context: Optional[str] = None  # Unused, kept for backwards compatibility
    ) -> Tweet:
        """Generate a single tweet (used for initial bot tweet).

        Note: _context parameter is accepted but unused. Tweet generation
        uses templates for speed. For context-aware batch generation,
        use _generate_tweets_batch() instead.
        """
        return self._generate_tweet_template(persona, token, state)

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
                (f"just market bought ${token.ticker} with my rent money. landlord can wait", 0.9),
                (f"${token.ticker} is giving me 2021 vibes fr fr", 0.6),
                (f"imagine not buying ${token.ticker} rn. ngmi", 0.7),
            ],
            PersonaType.SKEPTIC: [
                (f"${token.ticker} - anon team, no audit, unlocked LP. Classic rug setup.", -0.8),
                (f"Why would anyone buy ${token.ticker}? Genuine question.", -0.5),
                (f"${token.ticker} holders are exit liquidity. DYOR.", -0.7),
                (f"${token.ticker} tokenomics are trash. 90% team wallet btw", -0.9),
                (f"another day another ${token.ticker} shill. how original", -0.4),
                (f"${token.ticker}? more like ${token.ticker[0]}UG amirite", -0.8),
            ],
            PersonaType.WHALE: [
                (f"watching ${token.ticker}", 0.3),
                (f"${token.ticker}. interesting.", 0.4),
                (f"hmm ${token.ticker}", 0.2),
                (f"added ${token.ticker} to my watchlist", 0.5),
                ("...", 0.1),
            ],
            PersonaType.INFLUENCER: [
                (f"Just found ${token.ticker} - this could be big. Early alpha for my followers 👀", 0.8),
                (f"${token.ticker} thread coming soon. You're not ready.", 0.6),
                (f"CT is sleeping on ${token.ticker}. Don't say I didn't warn you.", 0.7),
                (f"Been researching ${token.ticker} all week. Here's why I'm bullish 🧵", 0.8),
                (f"${token.ticker} just hit my radar. Dev is based, community is strong.", 0.7),
            ],
            PersonaType.NORMIE: [
                (f"Is ${token.ticker} legit? Should I buy?", 0.2),
                (f"Just bought some ${token.ticker}, hope this moons!", 0.5),
                (f"What's the deal with ${token.ticker}?", 0.0),
                (f"my friend told me to buy ${token.ticker}. is it too late?", 0.3),
                (f"how do I even buy ${token.ticker}?? someone help", 0.1),
            ],
            PersonaType.BOT: [
                (f"🚨 NEW TOKEN: ${token.ticker}\nHolders: {random.randint(50, 500)}\nVol: ${random.randint(10, 100)}K", 0.0),
                (f"📊 ${token.ticker} 24h: +{random.randint(10, 500)}%\nMC: ${random.randint(100, 999)}K", 0.0),
            ],
            PersonaType.KOL: [
                (f"${token.ticker} has that special something. Reminds me of early $DOGE.", 0.7),
                (f"Did my DD on ${token.ticker}. Strong fundamentals for a memecoin.", 0.6),
                (f"${token.ticker} narrative is compelling. Worth a small position.", 0.5),
                (f"I'm seeing ${token.ticker} everywhere. Social metrics looking good.", 0.6),
                (f"${token.ticker} - not financial advice but I'm personally bullish here.", 0.7),
                (f"The ${token.ticker} community reminds me of early $SHIB. Just saying.", 0.8),
            ],
        }

        options = templates.get(persona.type, [(f"Interesting project ${token.ticker}", 0.3)])
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

    # --- Interaction Logic (replies/quotes) ---

    MAX_THREAD_DEPTH = 3
    INTERACTION_RATE = 0.15  # ~15% of tweets are interactions (light rate)
    MAX_HOT_TWEETS = 5  # Limit hot tweets per hour to prevent explosion

    def _identify_hot_tweets(self, state: SimulationState) -> list[Tweet]:
        """Find tweets likely to generate replies (high engagement, controversial, influential)."""
        # Look at tweets from last 2 hours
        recent_tweets = [
            t for t in state.tweets
            if t.hour >= state.current_hour - 2
            and t.thread_depth < self.MAX_THREAD_DEPTH
        ]

        scored_tweets = []
        for tweet in recent_tweets:
            # Engagement score (normalized)
            engagement_score = (tweet.likes + tweet.retweets) / 1000

            # Controversy score (extreme sentiment = more replies)
            controversy_score = abs(tweet.sentiment) * 0.5

            # Influence bonus (whale/influencer posts attract replies)
            influence_bonus = 0.3 if tweet.author.type in [
                PersonaType.WHALE, PersonaType.INFLUENCER, PersonaType.KOL
            ] else 0

            total_score = engagement_score + controversy_score + influence_bonus
            scored_tweets.append((tweet, total_score))

        # Sort by score and return top N
        scored_tweets.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in scored_tweets[:self.MAX_HOT_TWEETS]]

    def _select_interactions(
        self,
        state: SimulationState,
        hot_tweets: list[Tweet]
    ) -> list[tuple[Persona, Tweet, TweetType]]:
        """Select which personas will interact with which tweets."""
        interactions = []

        if not hot_tweets:
            return interactions

        # Calculate target number of interactions (10-20% of expected tweets)
        target_interactions = max(1, int(len(self.personas) * state.awareness * self.INTERACTION_RATE))

        for _ in range(target_interactions):
            # Pick a random hot tweet
            target_tweet = random.choice(hot_tweets)

            # Pick a persona that might reply (not the author)
            available_personas = [p for p in self.personas if p.handle != target_tweet.author.handle]
            if not available_personas:
                continue

            persona = random.choice(available_personas)

            # Check if this persona would reply based on dynamics
            reply_prob = self._calculate_reply_probability(persona, target_tweet, state)
            if random.random() > reply_prob:
                continue

            # Decide reply vs quote
            tweet_type = self._decide_interaction_type(persona, target_tweet)
            interactions.append((persona, target_tweet, tweet_type))

        return interactions

    def _calculate_reply_probability(
        self,
        persona: Persona,
        target_tweet: Tweet,
        state: SimulationState
    ) -> float:
        """Calculate probability that a persona replies to a tweet."""
        base_rate = 0.3  # Base chance when selected

        # Engagement modifier
        engagement_score = (target_tweet.likes + target_tweet.retweets) / 1000
        engagement_mod = min(engagement_score * 0.2, 0.2)

        # Persona conflict dynamics (balanced as per user preference)
        conflict_mod = 0.0
        if persona.type == PersonaType.SKEPTIC and target_tweet.sentiment > 0.5:
            conflict_mod = 0.15  # Skeptics challenge bullish takes
        elif persona.type == PersonaType.DEGEN and target_tweet.author.type == PersonaType.WHALE:
            conflict_mod = 0.15  # Degens hype whale posts
        elif persona.type == PersonaType.NORMIE:
            conflict_mod = 0.1  # Normies ask questions
        elif persona.type == PersonaType.INFLUENCER and target_tweet.author.type == PersonaType.WHALE:
            conflict_mod = 0.15  # Influencers amplify whales

        # Sentiment polarization (extreme sentiment attracts replies)
        sentiment_mod = abs(target_tweet.sentiment) * 0.1

        # Thread depth penalty (less likely to reply deep in threads)
        depth_penalty = target_tweet.thread_depth * 0.1

        return min(base_rate + engagement_mod + conflict_mod + sentiment_mod - depth_penalty, 0.6)

    def _decide_interaction_type(self, persona: Persona, target_tweet: Tweet) -> TweetType:
        """Decide whether persona should reply or quote-tweet."""
        # Influencers and KOLs prefer quotes (builds their profile)
        if persona.type in [PersonaType.INFLUENCER, PersonaType.KOL]:
            return TweetType.QUOTE if random.random() < 0.5 else TweetType.REPLY

        # Skeptics quote to expose/critique publicly
        if persona.type == PersonaType.SKEPTIC and target_tweet.sentiment > 0.5:
            return TweetType.QUOTE if random.random() < 0.6 else TweetType.REPLY

        # Normies mostly reply
        if persona.type == PersonaType.NORMIE:
            return TweetType.REPLY

        # Default: slight preference for replies
        return TweetType.REPLY if random.random() < 0.7 else TweetType.QUOTE

    def _generate_interactions_batch(
        self,
        interactions: list[tuple[Persona, Tweet, TweetType]],
        token: Token,
        state: SimulationState
    ) -> list[Tweet]:
        """Generate reply and quote tweets for selected interactions."""
        if not interactions:
            return []

        if not self.client:
            # Fallback to template interactions
            return [
                self._generate_interaction_template(persona, target, tweet_type, token, state)
                for persona, target, tweet_type in interactions
            ]

        # Build batch prompt for all interactions
        interaction_specs = []
        for i, (persona, target, tweet_type) in enumerate(interactions):
            relationship = self._describe_relationship(persona, target.author)
            spec = f"""Interaction {i + 1}:
Original by @{target.author.handle} ({target.author.type.value}): "{target.content}"
{tweet_type.value.upper()} from @{persona.handle} ({persona.type.value})
Relationship: {relationship}"""
            interaction_specs.append(spec)

        system_prompt = """You are simulating Crypto Twitter interactions.
Generate realistic REPLIES and QUOTE TWEETS. Match each persona's voice:
- degen: Supportive, apes in, "ser", "wagmi", often agrees with bullish takes
- skeptic: Challenges claims, asks hard questions, "source?", "anon team btw"
- whale: Minimal, cryptic, might just say "..." or "interesting"
- influencer: Adds context, builds narrative, subtle flex
- normie: Asks clarifying questions, unsure, "is this good?"
- kol: Gives opinion with authority, may agree or disagree thoughtfully
- bot: Stats, alerts only

REPLIES are short (under 140 chars), directly responding.
QUOTES add commentary (100-200 chars), can stand alone."""

        user_prompt = f"""Token: ${token.ticker} - {token.name}
CT mood: {"bullish" if state.momentum > 0.3 else "bearish" if state.momentum < -0.3 else "neutral"}

Generate these interactions:
{chr(10).join(interaction_specs)}

Return as JSON array:
[{{"index": 0, "content": "reply/quote text", "sentiment": 0.5}}]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=1.2,  # Higher temp for more varied replies/quotes
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text

            # Parse JSON array
            match = re.search(r'\[[\s\S]*\]', raw)
            if match:
                responses_data = json.loads(match.group())
            else:
                logger.warning("No JSON array in interaction response, using templates")
                responses_data = []

            # Create tweets from responses
            index_to_data = {r.get("index", i): r for i, r in enumerate(responses_data)}
            tweets = []

            for i, (persona, target, tweet_type) in enumerate(interactions):
                data = index_to_data.get(i, {})
                content = data.get("content", "")
                sentiment = float(data.get("sentiment", 0))

                if not content:
                    tweet = self._generate_interaction_template(persona, target, tweet_type, token, state)
                else:
                    tweet = self._create_interaction_tweet(
                        persona, content, sentiment, target, tweet_type, state
                    )
                tweets.append(tweet)

            return tweets

        except Exception as e:
            logger.warning(f"LLM interaction generation failed: {e}")
            return [
                self._generate_interaction_template(persona, target, tweet_type, token, state)
                for persona, target, tweet_type in interactions
            ]

    def _describe_relationship(self, replier: Persona, author: Persona) -> str:
        """Describe the relationship/dynamic between two personas."""
        if replier.type == PersonaType.SKEPTIC:
            if author.type in [PersonaType.DEGEN, PersonaType.INFLUENCER]:
                return "challenges bullish narratives"
            return "questions everything"
        elif replier.type == PersonaType.DEGEN:
            if author.type == PersonaType.WHALE:
                return "follows whale activity closely"
            return "adds to the hype"
        elif replier.type == PersonaType.NORMIE:
            return "trying to understand"
        elif replier.type == PersonaType.INFLUENCER:
            if author.type == PersonaType.WHALE:
                return "amplifies whale signals"
            return "building narrative"
        return "engaging"

    def _create_interaction_tweet(
        self,
        persona: Persona,
        content: str,
        sentiment: float,
        target: Tweet,
        tweet_type: TweetType,
        state: SimulationState
    ) -> Tweet:
        """Create an interaction tweet (reply or quote)."""
        # Lower engagement for replies/quotes vs original tweets
        base_engagement = int(persona.influence_score * 500)
        momentum_multiplier = 1 + (state.momentum * 0.3)

        return Tweet(
            id=f"tweet_{state.current_hour}_{persona.handle}_{tweet_type.value}",
            author=persona,
            content=content,
            hour=state.current_hour,
            likes=int(base_engagement * momentum_multiplier * random.uniform(0.3, 1.2)),
            retweets=int(base_engagement * 0.2 * momentum_multiplier * random.uniform(0.2, 1.0)),
            replies=int(base_engagement * 0.1 * random.uniform(0.3, 1.5)),
            sentiment=max(-1, min(1, sentiment)),
            tweet_type=tweet_type,
            is_reply_to=target.id if tweet_type == TweetType.REPLY else None,
            quotes_tweet=target.id if tweet_type == TweetType.QUOTE else None,
            thread_depth=target.thread_depth + 1,
        )

    def _generate_interaction_template(
        self,
        persona: Persona,
        target: Tweet,
        tweet_type: TweetType,
        token: Token,
        state: SimulationState
    ) -> Tweet:
        """Generate interaction using templates (fallback)."""
        reply_templates = {
            PersonaType.DEGEN: [
                ("ser this is the way", 0.7),
                ("absolutely based", 0.8),
                ("LFG 🚀", 0.9),
                ("wagmi fren", 0.8),
                ("this guy gets it", 0.7),
                ("bullish af on this take", 0.8),
                ("wen moon ser", 0.6),
            ],
            PersonaType.SKEPTIC: [
                ("source?", -0.3),
                ("how is this different from every other rug?", -0.7),
                ("anon team btw", -0.5),
                ("have fun staying poor i guess", -0.6),
                ("this aged well", -0.4),
                ("remind me in 2 weeks", -0.5),
                ("cope", -0.6),
            ],
            PersonaType.WHALE: [
                ("...", 0.1),
                ("interesting", 0.2),
                ("noted", 0.3),
                ("👀", 0.2),
            ],
            PersonaType.INFLUENCER: [
                ("Adding this to my watchlist", 0.5),
                ("This thread needs more context 👇", 0.4),
                ("Great alpha here", 0.6),
                ("My followers need to see this", 0.7),
                ("Saving this for later", 0.5),
            ],
            PersonaType.NORMIE: [
                ("Wait is this good?", 0.1),
                ("Should I buy?", 0.2),
                ("Can someone explain?", 0.0),
                ("I don't understand but I'm in", 0.4),
                ("what does this mean for my bag?", 0.2),
            ],
            PersonaType.KOL: [
                ("Interesting take. Here's my view:", 0.3),
                ("Worth watching this one", 0.4),
                ("I've been saying this for weeks", 0.5),
                ("The data supports this", 0.6),
                ("Solid analysis here", 0.5),
            ],
            PersonaType.BOT: [
                ("🔔 Alert triggered", 0.0),
                ("📈 Tracking this", 0.0),
            ],
        }

        quote_templates = {
            PersonaType.DEGEN: [
                (f"CT is waking up to ${token.ticker}. Early gang knows.", 0.8),
                (f"${token.ticker} believers where you at 🚀", 0.9),
                (f"this is why I'm all in on ${token.ticker}", 0.8),
            ],
            PersonaType.SKEPTIC: [
                (f"And this is why you DYOR on ${token.ticker}. Red flags everywhere.", -0.7),
                (f"${token.ticker} maxis coping hard rn", -0.6),
                (f"imagine believing ${token.ticker} is going anywhere", -0.8),
            ],
            PersonaType.INFLUENCER: [
                (f"Let me add some context on ${token.ticker} for my followers 👇", 0.5),
                (f"${token.ticker} alpha that CT isn't talking about:", 0.7),
                (f"Important ${token.ticker} thread from a reliable source", 0.6),
            ],
            PersonaType.KOL: [
                (f"My thoughts on ${token.ticker} and this take:", 0.5),
                (f"${token.ticker} analysis - here's what I'm seeing:", 0.6),
            ],
            PersonaType.NORMIE: [
                (f"is ${token.ticker} really doing this??", 0.3),
                (f"someone explain ${token.ticker} to me like I'm 5", 0.1),
            ],
            PersonaType.WHALE: [
                (f"${token.ticker}", 0.3),
                ("👀", 0.2),
            ],
        }

        templates = quote_templates if tweet_type == TweetType.QUOTE else reply_templates
        options = templates.get(persona.type, [("interesting take", 0.2)])
        content, sentiment = random.choice(options)

        return self._create_interaction_tweet(persona, content, sentiment, target, tweet_type, state)

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

            # Phase 1: Generate original tweets in batch
            new_tweets = self._generate_tweets_batch(active_personas, token, state, context)

            # Phase 2: Generate interactions (replies/quotes) to hot tweets
            hot_tweets = self._identify_hot_tweets(state)
            interactions = self._select_interactions(state, hot_tweets)
            interaction_tweets = self._generate_interactions_batch(interactions, token, state)
            new_tweets.extend(interaction_tweets)

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
            "tweet": self._tweet_to_dict(initial_tweet, state.tweets),
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

            # Phase 1: Generate original tweets in batch
            new_tweets = self._generate_tweets_batch(active_personas, token, state, context)

            # Yield original tweets
            for tweet in new_tweets:
                yield {
                    "type": "tweet",
                    "tweet": self._tweet_to_dict(tweet, state.tweets),
                }

            # Phase 2: Generate interactions (replies/quotes) to hot tweets
            hot_tweets = self._identify_hot_tweets(state)
            interactions = self._select_interactions(state, hot_tweets)
            interaction_tweets = self._generate_interactions_batch(interactions, token, state)

            # Yield interaction tweets
            for tweet in interaction_tweets:
                yield {
                    "type": "tweet",
                    "tweet": self._tweet_to_dict(tweet, state.tweets + new_tweets),
                }

            new_tweets.extend(interaction_tweets)

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

    def _tweet_to_dict(self, tweet: Tweet, all_tweets: Optional[list[Tweet]] = None) -> dict:
        """Convert a Tweet to a serializable dict."""
        result = {
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
            "tweet_type": tweet.tweet_type.value,
            "is_reply_to": tweet.is_reply_to,
            "quotes_tweet": tweet.quotes_tweet,
            "thread_depth": tweet.thread_depth,
        }

        # Denormalize parent/quoted tweet info for UI
        if all_tweets:
            tweet_map = {t.id: t for t in all_tweets}

            if tweet.is_reply_to and tweet.is_reply_to in tweet_map:
                parent = tweet_map[tweet.is_reply_to]
                result["reply_to_author"] = parent.author.handle

            if tweet.quotes_tweet and tweet.quotes_tweet in tweet_map:
                quoted = tweet_map[tweet.quotes_tweet]
                result["quoted_content"] = quoted.content[:100]
                result["quoted_author"] = quoted.author.handle

        return result

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
