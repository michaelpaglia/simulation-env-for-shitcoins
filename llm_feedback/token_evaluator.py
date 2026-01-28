"""
Token Concept Evaluator

Uses the CT simulation + LLM feedback to evaluate whether a shitcoin
concept would perform well before deploying it.

Flow:
1. Define token concept (name, ticker, narrative, meme style)
2. Run synthetic CT simulation (informed by real Twitter priors)
3. LLM observes simulation and evaluates the concept
4. Get actionable feedback on what to change
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import json

from .observer import SimulationObserver
from .analyzer import LLMAnalyzer, Analysis
from .feedback_loop import FeedbackLoop, LoopConfig


@dataclass
class TokenConcept:
    """A shitcoin concept to evaluate."""
    name: str
    ticker: str
    narrative: str  # e.g., "AI-powered dog coin"
    meme_style: str = "ironic"  # ironic, sincere, absurdist
    target_audience: str = "degens"  # degens, normies, tech crowd
    hook: str = ""  # The viral hook / unique angle

    # Optional priors from real Twitter data
    similar_tokens_sentiment: Optional[float] = None  # How similar tokens performed
    current_ct_mood: Optional[str] = None  # Current CT meta (bullish, bearish, etc.)

    def to_prompt(self) -> str:
        return f"""Token: {self.name} (${self.ticker})
Narrative: {self.narrative}
Meme Style: {self.meme_style}
Target Audience: {self.target_audience}
Hook: {self.hook or 'None specified'}
CT Context: {self.current_ct_mood or 'Unknown'}"""


@dataclass
class ConceptFeedback:
    """Feedback on a token concept from the LLM."""
    viability_score: float  # 0-1, would this work on CT?
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]  # Concrete changes to try
    predicted_outcome: str  # moon, pump_and_dump, slow_bleed, etc.
    reasoning: str
    confidence: float


EVALUATOR_PROMPT = """You are a Crypto Twitter (CT) analyst evaluating shitcoin concepts.

You're watching a SYNTHETIC simulation of how CT would react to a new token.
Your job is to evaluate the TOKEN CONCEPT itself - would this actually work on CT?

Based on the simulation data, assess:

1. **Narrative Strength**: Is the story compelling? Does it have meme potential?
2. **Hook Quality**: Is there a viral angle that makes people want to share?
3. **Audience Fit**: Does this resonate with the target audience?
4. **FUD Vulnerability**: What are the obvious attack vectors?
5. **Timing**: Does this fit the current CT meta/mood?

Respond in JSON:
{
    "viability_score": 0.0-1.0,
    "strengths": ["what's working"],
    "weaknesses": ["what's not working"],
    "suggestions": ["specific changes to try - be concrete"],
    "predicted_outcome": "moon|cult_classic|pump_and_dump|slow_bleed|dead_on_arrival",
    "reasoning": "your analysis",
    "confidence": 0.0-1.0
}

Be brutally honest. Most shitcoins fail. Only give high scores if the concept genuinely has potential."""


class TokenEvaluator:
    """
    Evaluates token concepts using synthetic CT simulation + LLM feedback.

    This is the main interface for testing shitcoin ideas before deployment.
    """

    def __init__(
        self,
        simulation_engine,  # The CT simulation engine
        model: str = "claude-sonnet-4-20250514",
    ):
        self.simulation_engine = simulation_engine
        self.analyzer = LLMAnalyzer(
            system_prompt=EVALUATOR_PROMPT,
            model=model,
        )
        self.evaluation_history: list[tuple[TokenConcept, ConceptFeedback]] = []

    def evaluate(
        self,
        concept: TokenConcept,
        simulation_hours: int = 24,
        checkpoints: int = 3,  # How many times to check during simulation
    ) -> ConceptFeedback:
        """
        Run a synthetic CT simulation and evaluate the token concept.

        Args:
            concept: The token concept to evaluate
            simulation_hours: How long to simulate (in CT hours)
            checkpoints: Number of LLM evaluations during the run
        """
        # Build simulation context
        sim_state = {
            "concept": concept,
            "hours_elapsed": 0,
            "tweets": [],
            "sentiment_history": [],
            "engagement_total": 0,
            "fud_events": [],
            "influencer_mentions": 0,
        }

        # Run simulation with periodic LLM checks
        checkpoint_interval = simulation_hours // checkpoints
        intermediate_feedback = []

        for hour in range(simulation_hours):
            # Advance simulation (this would call actual engine)
            sim_state = self._simulate_hour(sim_state, concept)

            # Checkpoint evaluation
            if (hour + 1) % checkpoint_interval == 0:
                context = self._build_context(concept, sim_state)
                analysis = self.analyzer.analyze(context)
                intermediate_feedback.append(analysis)

        # Final evaluation
        final_context = self._build_final_context(concept, sim_state, intermediate_feedback)
        final_analysis = self.analyzer.analyze(final_context)

        feedback = self._parse_feedback(final_analysis)
        self.evaluation_history.append((concept, feedback))

        return feedback

    def quick_evaluate(self, concept: TokenConcept) -> ConceptFeedback:
        """
        Quick concept evaluation without full simulation.
        Just asks LLM to evaluate the concept directly.
        """
        context = f"""Evaluate this token concept for CT viability:

{concept.to_prompt()}

No simulation data yet - just evaluate the concept on its merits.
Would this have potential on Crypto Twitter? Why or why not?"""

        analysis = self.analyzer.analyze(context)
        return self._parse_feedback(analysis)

    def iterate(
        self,
        concept: TokenConcept,
        previous_feedback: ConceptFeedback,
    ) -> list[TokenConcept]:
        """
        Generate improved concept variations based on feedback.
        """
        context = f"""Based on this feedback, generate 2-3 improved variations:

Original Concept:
{concept.to_prompt()}

Feedback:
- Viability: {previous_feedback.viability_score:.0%}
- Weaknesses: {previous_feedback.weaknesses}
- Suggestions: {previous_feedback.suggestions}

Return JSON with variations:
{{
    "variations": [
        {{"name": "...", "ticker": "...", "narrative": "...", "hook": "...", "changes": "what you changed"}}
    ]
}}"""

        response = self.analyzer.client.messages.create(
            model=self.analyzer.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": context}],
        )

        # Parse variations
        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            data = json.loads(text[start:end])

            variations = []
            for v in data.get("variations", []):
                variations.append(TokenConcept(
                    name=v.get("name", concept.name),
                    ticker=v.get("ticker", concept.ticker),
                    narrative=v.get("narrative", concept.narrative),
                    meme_style=v.get("meme_style", concept.meme_style),
                    target_audience=v.get("target_audience", concept.target_audience),
                    hook=v.get("hook", ""),
                    current_ct_mood=concept.current_ct_mood,
                ))
            return variations
        except:
            return []

    def _simulate_hour(self, state: dict, concept: TokenConcept) -> dict:
        """Simulate one hour of CT activity. Override with actual engine."""
        # Placeholder - would integrate with actual SimulationEngine
        import random

        state["hours_elapsed"] += 1

        # Fake sentiment evolution
        sentiment = 0.5 + random.gauss(0, 0.1)
        state["sentiment_history"].append(sentiment)

        # Fake engagement
        state["engagement_total"] += random.randint(10, 100)

        return state

    def _build_context(self, concept: TokenConcept, state: dict) -> str:
        """Build context string for LLM analysis."""
        recent_sentiment = state["sentiment_history"][-5:] if state["sentiment_history"] else []
        avg_sentiment = sum(recent_sentiment) / len(recent_sentiment) if recent_sentiment else 0.5

        return f"""Token Concept:
{concept.to_prompt()}

Simulation State (Hour {state['hours_elapsed']}):
- Average Sentiment: {avg_sentiment:.2f}
- Total Engagement: {state['engagement_total']}
- Influencer Mentions: {state['influencer_mentions']}
- FUD Events: {len(state['fud_events'])}
- Sentiment Trend: {recent_sentiment}"""

    def _build_final_context(
        self,
        concept: TokenConcept,
        state: dict,
        intermediate: list[Analysis],
    ) -> str:
        """Build final evaluation context."""
        base = self._build_context(concept, state)

        if intermediate:
            prev_observations = [a.observations for a in intermediate if a.observations]
            base += f"\n\nPrevious Observations During Simulation:\n"
            for i, obs in enumerate(prev_observations):
                base += f"Checkpoint {i+1}: {obs}\n"

        base += "\n\nProvide your FINAL evaluation of this token concept."
        return base

    def _parse_feedback(self, analysis: Analysis) -> ConceptFeedback:
        """Parse LLM analysis into ConceptFeedback."""
        try:
            # Try to extract structured data from raw response
            text = analysis.raw_response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                return ConceptFeedback(
                    viability_score=data.get("viability_score", 0.5),
                    strengths=data.get("strengths", []),
                    weaknesses=data.get("weaknesses", []),
                    suggestions=data.get("suggestions", []),
                    predicted_outcome=data.get("predicted_outcome", "unknown"),
                    reasoning=data.get("reasoning", ""),
                    confidence=data.get("confidence", 0.5),
                )
        except:
            pass

        # Fallback
        return ConceptFeedback(
            viability_score=0.5,
            strengths=analysis.observations,
            weaknesses=analysis.concerns,
            suggestions=[r.get("reason", "") for r in analysis.recommendations],
            predicted_outcome="unknown",
            reasoning=analysis.reasoning,
            confidence=analysis.confidence,
        )
