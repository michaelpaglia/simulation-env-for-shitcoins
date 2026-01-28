"""
CT Simulation Integration

Connects the LLM feedback loop to the actual CT simulation engine.
Runs synthetic simulations and evaluates token concepts.
"""

import os
from dataclasses import dataclass
from typing import Optional, Callable
import json

# Import the actual simulation engine
from src.simulation.engine import SimulationEngine, SimulationState, Tweet
from src.models.token import Token, SimulationResult, MarketCondition, MemeStyle
from src.agents.personas import PersonaType

from .observer import SimulationObserver
from .analyzer import LLMAnalyzer, Analysis
from .feedback_loop import FeedbackLoop, LoopConfig, LoopIteration
from .token_evaluator import TokenConcept, ConceptFeedback


def concept_to_token(concept: TokenConcept) -> Token:
    """Convert a TokenConcept to the simulation Token model."""

    # Map meme style
    style_map = {
        "ironic": MemeStyle.ABSURD,
        "sincere": MemeStyle.CUTE,
        "absurdist": MemeStyle.ABSURD,
        "edgy": MemeStyle.EDGY,
        "topical": MemeStyle.TOPICAL,
    }
    meme_style = style_map.get(concept.meme_style, MemeStyle.ABSURD)

    # Map CT mood to market condition
    mood_map = {
        "bullish": MarketCondition.BULL,
        "bearish": MarketCondition.BEAR,
        "euphoria": MarketCondition.EUPHORIA,
    }
    market = MarketCondition.CRAB
    if concept.current_ct_mood:
        for key, val in mood_map.items():
            if key in concept.current_ct_mood.lower():
                market = val
                break

    return Token(
        name=concept.name,
        ticker=concept.ticker,
        narrative=concept.narrative,
        meme_style=meme_style,
        tagline=concept.hook or None,
        market_condition=market,
    )


@dataclass
class SimulationSnapshot:
    """Snapshot of CT simulation state for LLM analysis."""
    hour: int
    sentiment: float
    momentum: float
    awareness: float
    total_engagement: int
    total_mentions: int
    influencer_mentions: int
    recent_tweets: list[dict]
    sentiment_history: list[float]

    def to_dict(self) -> dict:
        return {
            "hour": self.hour,
            "sentiment": round(self.sentiment, 3),
            "momentum": round(self.momentum, 3),
            "awareness": round(self.awareness, 3),
            "total_engagement": self.total_engagement,
            "total_mentions": self.total_mentions,
            "influencer_mentions": self.influencer_mentions,
            "recent_tweets": self.recent_tweets,
            "sentiment_trend": self.sentiment_history[-5:] if self.sentiment_history else [],
        }


CT_EVALUATOR_PROMPT = """You are a Crypto Twitter analyst evaluating a token launch simulation.

You're watching a SYNTHETIC simulation of how CT personas would react to this token.
The simulation generates realistic tweets from degens, skeptics, whales, influencers, etc.

Your job: evaluate the TOKEN CONCEPT based on how the simulation is unfolding.

Key metrics to watch:
- **momentum**: Current viral momentum (-1 to 1). Above 0.3 = bullish, below -0.3 = bearish
- **awareness**: What % of CT knows about this token (0-1)
- **sentiment**: Average sentiment of recent tweets
- **influencer_mentions**: Key for virality

Evaluate:
1. Is the narrative catching on? (look at tweet content and sentiment)
2. Is it generating organic engagement or dying?
3. Are influencers picking it up?
4. What FUD is emerging and is it sticking?
5. Would you change anything about the concept?

Respond in JSON:
{
    "status": "thriving|growing|stagnant|declining|dying",
    "observations": ["what you notice about CT's reaction"],
    "concept_strengths": ["what's working about the token concept"],
    "concept_weaknesses": ["what's not working"],
    "emerging_fud": ["FUD narratives gaining traction"],
    "suggestions": ["specific changes to the concept to try"],
    "viability_score": 0.0-1.0,
    "predicted_outcome": "moon|cult_classic|pump_and_dump|slow_bleed|dead_on_arrival",
    "reasoning": "your analysis",
    "confidence": 0.0-1.0
}"""


class CTSimulationRunner:
    """
    Runs the CT simulation with LLM feedback loop integration.

    This wraps SimulationEngine to provide:
    - Hour-by-hour stepping (instead of running all at once)
    - State observation for LLM analysis
    - Concept evaluation based on simulation results
    """

    def __init__(self, api_key: Optional[str] = None, use_llm_tweets: bool = False):
        """
        Args:
            api_key: Anthropic API key
            use_llm_tweets: If True, use LLM for tweet generation (slower, uses more API).
                           If False, use template-based tweets (faster, saves API for analysis).
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        # Only pass API key to engine if we want LLM-generated tweets
        self.engine = SimulationEngine(api_key=self.api_key if use_llm_tweets else None)
        self.analyzer = LLMAnalyzer(
            system_prompt=CT_EVALUATOR_PROMPT,
            model="claude-sonnet-4-20250514",
            api_key=self.api_key,
        )

        self.state: Optional[SimulationState] = None
        self.token: Optional[Token] = None
        self.concept: Optional[TokenConcept] = None
        self.analyses: list[Analysis] = []

    def initialize(self, concept: TokenConcept) -> None:
        """Initialize a new simulation run."""
        self.concept = concept
        self.token = concept_to_token(concept)
        self.state = SimulationState(token=self.token)
        self.analyses = []

        # Initial seeding - bot alerts first
        from src.agents.personas import get_persona
        bot = get_persona(PersonaType.BOT)
        initial_tweet = self.engine._generate_tweet(bot, self.token, self.state)
        self.engine._update_state(self.state, [initial_tweet])

    def step(self) -> bool:
        """
        Advance simulation by one hour.
        Returns False if simulation should end.
        """
        if self.state is None:
            raise RuntimeError("Call initialize() first")

        # Select active personas and generate tweets
        active_personas = self.engine._select_active_personas(self.state)

        # Get recent context
        recent_tweets = self.state.tweets[-5:] if self.state.tweets else []
        context = "\n".join(f"@{t.author.handle}: {t.content}" for t in recent_tweets)

        # Generate tweets
        new_tweets = [
            self.engine._generate_tweet(persona, self.token, self.state, context)
            for persona in active_personas
        ]

        self.engine._update_state(self.state, new_tweets)

        # Check for death
        if self.state.momentum < -0.7 and self.state.awareness < 0.3 and self.state.current_hour > 12:
            return False

        return True

    def get_snapshot(self) -> SimulationSnapshot:
        """Get current simulation state as a snapshot."""
        if self.state is None:
            raise RuntimeError("Call initialize() first")

        recent_tweets = []
        for t in self.state.tweets[-10:]:
            recent_tweets.append({
                "author": t.author.handle,
                "type": t.author.type.value,
                "content": t.content,
                "sentiment": round(t.sentiment, 2),
                "engagement": t.likes + t.retweets + t.replies,
            })

        current_sentiment = (
            self.state.sentiment_history[-1]
            if self.state.sentiment_history
            else 0.0
        )

        return SimulationSnapshot(
            hour=self.state.current_hour,
            sentiment=current_sentiment,
            momentum=self.state.momentum,
            awareness=self.state.awareness,
            total_engagement=self.state.total_engagement,
            total_mentions=self.state.total_mentions,
            influencer_mentions=self.state.influencer_mentions,
            recent_tweets=recent_tweets,
            sentiment_history=list(self.state.sentiment_history),
        )

    def get_metrics(self) -> dict:
        """Get current metrics dict for observer."""
        snapshot = self.get_snapshot()
        return snapshot.to_dict()

    def get_state_dict(self) -> dict:
        """Get full state dict."""
        if self.state is None:
            return {}
        return {
            "hour": self.state.current_hour,
            "momentum": self.state.momentum,
            "awareness": self.state.awareness,
            "total_tweets": len(self.state.tweets),
        }

    def get_recent_tweets(self) -> list[dict]:
        """Get recent tweets as dicts."""
        snapshot = self.get_snapshot()
        return snapshot.recent_tweets

    def compile_results(self) -> SimulationResult:
        """Compile final simulation results."""
        if self.state is None:
            raise RuntimeError("No simulation state")
        return self.engine._compile_results(self.state)


class CTConceptEvaluator:
    """
    Main interface for evaluating token concepts using CT simulation + LLM feedback.

    Usage:
        evaluator = CTConceptEvaluator()
        feedback = evaluator.evaluate(concept, hours=24, analyze_every=6)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.runner = CTSimulationRunner(api_key=self.api_key)

    def evaluate(
        self,
        concept: TokenConcept,
        hours: int = 48,
        analyze_every: int = 8,
        verbose: bool = True,
        on_analysis: Optional[Callable[[int, Analysis], None]] = None,
    ) -> tuple[SimulationResult, ConceptFeedback]:
        """
        Run full CT simulation with LLM analysis checkpoints.

        Args:
            concept: Token concept to evaluate
            hours: Simulation duration in CT hours
            analyze_every: Run LLM analysis every N hours
            verbose: Print progress
            on_analysis: Callback for each analysis (hour, analysis)

        Returns:
            (SimulationResult, ConceptFeedback) - simulation metrics + concept evaluation
        """
        self.runner.initialize(concept)

        if verbose:
            print(f"\nSimulating ${concept.ticker} on CT for {hours} hours...")
            print("-" * 50)

        # Set up observer
        observer = SimulationObserver(
            state_extractor=self.runner.get_state_dict,
            metrics_extractor=self.runner.get_metrics,
            events_extractor=self.runner.get_recent_tweets,
        )

        analyses = []

        for hour in range(1, hours + 1):
            # Advance simulation
            alive = self.runner.step()

            # Observe
            observer.observe()

            # Print progress
            if verbose and hour % 6 == 0:
                m = self.runner.get_metrics()
                print(f"[Hour {hour:2d}] momentum={m['momentum']:+.2f} "
                      f"awareness={m['awareness']:.0%} "
                      f"engagement={m['total_engagement']:,}")

            # LLM analysis checkpoint
            if hour % analyze_every == 0:
                context = self._build_analysis_context(concept, observer)
                analysis = self.runner.analyzer.analyze(context)
                analyses.append((hour, analysis))

                if on_analysis:
                    on_analysis(hour, analysis)

                if verbose:
                    self._print_analysis(hour, analysis)

            if not alive:
                if verbose:
                    print(f"\n[Hour {hour}] Token died - momentum crashed")
                break

        # Compile results
        sim_result = self.runner.compile_results()

        # Final concept feedback
        concept_feedback = self._compile_concept_feedback(concept, sim_result, analyses)

        if verbose:
            print("\n" + "=" * 50)
            print("FINAL RESULTS")
            print("=" * 50)
            print(sim_result.summary())
            print("\nCONCEPT FEEDBACK")
            print(f"Viability: {concept_feedback.viability_score:.0%}")
            print(f"Predicted: {concept_feedback.predicted_outcome}")

        return sim_result, concept_feedback

    def quick_evaluate(self, concept: TokenConcept) -> ConceptFeedback:
        """Quick concept evaluation without full simulation."""
        context = f"""Evaluate this token concept for CT viability (no simulation):

Token: {concept.name} (${concept.ticker})
Narrative: {concept.narrative}
Hook: {concept.hook}
Style: {concept.meme_style}
Target: {concept.target_audience}
CT Mood: {concept.current_ct_mood or 'Unknown'}

Would this work on Crypto Twitter? Analyze the concept itself."""

        analysis = self.runner.analyzer.analyze(context)
        return self._parse_feedback(analysis)

    def _build_analysis_context(
        self,
        concept: TokenConcept,
        observer: SimulationObserver
    ) -> str:
        """Build context for LLM analysis."""
        metrics = self.runner.get_metrics()
        tweets = self.runner.get_recent_tweets()

        tweet_summary = "\n".join([
            f"  @{t['author']} ({t['type']}): \"{t['content'][:80]}...\" [sentiment: {t['sentiment']:+.1f}]"
            for t in tweets[-5:]
        ])

        return f"""TOKEN CONCEPT:
{concept.name} (${concept.ticker})
Narrative: {concept.narrative}
Hook: {concept.hook}

SIMULATION STATE (Hour {metrics['hour']}):
- Momentum: {metrics['momentum']:+.2f} {"(bullish)" if metrics['momentum'] > 0.3 else "(bearish)" if metrics['momentum'] < -0.3 else "(neutral)"}
- Awareness: {metrics['awareness']:.0%} of CT knows about it
- Total Engagement: {metrics['total_engagement']:,}
- Influencer Pickups: {metrics['influencer_mentions']}
- Sentiment Trend: {metrics['sentiment_trend']}

RECENT TWEETS:
{tweet_summary}

Analyze how CT is reacting to this token concept."""

    def _print_analysis(self, hour: int, analysis: Analysis):
        """Print analysis summary."""
        print(f"\n  [LLM Analysis @ Hour {hour}]")
        if analysis.observations:
            print(f"  Status: {analysis.observations[0] if analysis.observations else 'N/A'}")
        if analysis.concerns:
            print(f"  Concerns: {analysis.concerns[:2]}")

    def _compile_concept_feedback(
        self,
        concept: TokenConcept,
        sim_result: SimulationResult,
        analyses: list[tuple[int, Analysis]],
    ) -> ConceptFeedback:
        """Compile final concept feedback from simulation + analyses."""

        # Aggregate from analyses
        all_strengths = []
        all_weaknesses = []
        all_suggestions = []
        total_viability = 0

        for hour, analysis in analyses:
            try:
                data = json.loads(
                    analysis.raw_response[
                        analysis.raw_response.find("{"):
                        analysis.raw_response.rfind("}") + 1
                    ]
                )
                all_strengths.extend(data.get("concept_strengths", []))
                all_weaknesses.extend(data.get("concept_weaknesses", []))
                all_suggestions.extend(data.get("suggestions", []))
                total_viability += data.get("viability_score", 0.5)
            except:
                pass

        # Deduplicate
        strengths = list(dict.fromkeys(all_strengths))[:5]
        weaknesses = list(dict.fromkeys(all_weaknesses))[:5]
        suggestions = list(dict.fromkeys(all_suggestions))[:5]

        # Calculate final viability from simulation metrics
        viability = 0.5
        if sim_result.viral_coefficient > 1.5:
            viability += 0.2
        if sim_result.peak_sentiment > 0.5:
            viability += 0.1
        if sim_result.fud_resistance > 0.5:
            viability += 0.1
        if sim_result.influencer_pickups > 3:
            viability += 0.1
        if sim_result.hours_to_death:
            viability -= 0.3

        viability = max(0, min(1, viability))

        return ConceptFeedback(
            viability_score=viability,
            strengths=strengths or ["Simulation completed without major issues"],
            weaknesses=weaknesses or sim_result.top_fud_points,
            suggestions=suggestions or ["Consider stronger hook", "Refine narrative"],
            predicted_outcome=sim_result.predicted_outcome,
            reasoning=f"Based on {len(analyses)} analysis checkpoints over {sim_result.hours_to_peak + (sim_result.hours_to_death or 48)} hours. "
                      f"Viral coefficient: {sim_result.viral_coefficient:.2f}x, "
                      f"FUD resistance: {sim_result.fud_resistance:.0%}",
            confidence=sim_result.confidence,
        )

    def _parse_feedback(self, analysis: Analysis) -> ConceptFeedback:
        """Parse single analysis into ConceptFeedback."""
        try:
            text = analysis.raw_response
            data = json.loads(text[text.find("{"):text.rfind("}") + 1])
            return ConceptFeedback(
                viability_score=data.get("viability_score", 0.5),
                strengths=data.get("concept_strengths", []),
                weaknesses=data.get("concept_weaknesses", []),
                suggestions=data.get("suggestions", []),
                predicted_outcome=data.get("predicted_outcome", "unknown"),
                reasoning=data.get("reasoning", ""),
                confidence=data.get("confidence", 0.5),
            )
        except:
            return ConceptFeedback(
                viability_score=0.5,
                strengths=analysis.observations,
                weaknesses=analysis.concerns,
                suggestions=[],
                predicted_outcome="unknown",
                reasoning=analysis.reasoning,
                confidence=analysis.confidence,
            )
