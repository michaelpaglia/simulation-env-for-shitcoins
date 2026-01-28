"""
Synthetic Market Simulation Example

Demonstrates LLM feedback loop on a fully synthetic market simulation.
No real data used - all patterns are generated.

Run with: python -m llm_feedback.examples.synthetic_market
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from llm_feedback import SimulationObserver, LLMAnalyzer, FeedbackLoop, AdjustmentEngine
from llm_feedback.adjustments import AdjustmentConstraint
from llm_feedback.feedback_loop import LoopConfig
from llm_feedback.analyzer import Analysis
import random


class SyntheticMarketSim:
    """
    Synthetic market simulation - generates fake market patterns.

    No real data. Real data should only be used for training priors
    (e.g., what realistic volatility ranges look like), not runtime.
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.tick = 0
        self.price = 100.0
        self.sentiment = 0.5
        self.volatility = 0.03
        self.trend_strength = 0.01
        self.volume = 1000

    def step(self) -> bool:
        self.tick += 1

        trend = self.trend_strength * (self.sentiment - 0.5)
        noise = random.gauss(0, self.volatility)
        self.price = max(1, self.price * (1 + trend + noise))

        sentiment_noise = random.gauss(0, 0.05)
        self.sentiment = max(0, min(1, self.sentiment + sentiment_noise))

        self.volume = max(100, self.volume + random.randint(-200, 200))

        return self.tick < 30

    def get_state(self) -> dict:
        return {
            "tick": self.tick,
            "price": self.price,
            "sentiment": self.sentiment,
            "volatility": self.volatility,
            "trend_strength": self.trend_strength,
            "volume": self.volume,
        }

    def get_metrics(self) -> dict:
        return {
            "tick": self.tick,
            "price": round(self.price, 2),
            "sentiment": round(self.sentiment, 3),
            "volume": self.volume,
            "volatility": self.volatility,
        }

    def set_param(self, name: str, value):
        if hasattr(self, name):
            setattr(self, name, value)
            print(f"  [Adjusted] {name} = {value}")


ANALYSIS_PROMPT = """You are analyzing a SYNTHETIC market simulation (not real data).

Metrics:
- price: Current synthetic price (started at 100)
- sentiment: Market sentiment 0-1 (0.5 = neutral)
- volume: Synthetic trading volume
- volatility: Price noise level

Watch for:
1. Price crash (dropping too fast)
2. Sentiment collapse (below 0.3)
3. Volume death (very low activity)

You can recommend adjustments to:
- volatility (0.01 - 0.1)
- trend_strength (-0.05 to 0.05)

Respond in JSON:
{
    "observations": ["what you notice"],
    "concerns": ["issues if any"],
    "recommendations": [{"parameter": "x", "current": 0, "suggested": 0, "reason": "why"}],
    "reasoning": "your analysis",
    "confidence": 0.0-1.0
}"""


class MockAnalyzer:
    """Mock analyzer for testing without LLM API."""

    def analyze(self, context: str) -> Analysis:
        return Analysis(
            observations=["Synthetic data trending normally"],
            concerns=[],
            recommendations=[],
            reasoning="Mock analysis - no LLM call",
            confidence=0.7,
            raw_response="mock",
        )


def run(use_llm: bool = True, seed: int = 123):
    """Run the synthetic market simulation with feedback loop."""
    print("Synthetic Market Simulation with LLM Feedback")
    print("=" * 50)
    print("Note: All data is synthetic. Real data only for priors.\n")

    sim = SyntheticMarketSim(seed=seed)

    observer = SimulationObserver(
        state_extractor=sim.get_state,
        metrics_extractor=sim.get_metrics,
    )

    if use_llm:
        analyzer = LLMAnalyzer(
            system_prompt=ANALYSIS_PROMPT,
            model="claude-sonnet-4-20250514",
        )
    else:
        analyzer = MockAnalyzer()

    adjuster = AdjustmentEngine(
        param_getter=lambda p: getattr(sim, p, None),
        param_setter=sim.set_param,
    )
    adjuster.add_constraint("volatility", AdjustmentConstraint(min_value=0.01, max_value=0.1))
    adjuster.add_constraint("trend_strength", AdjustmentConstraint(min_value=-0.05, max_value=0.05))

    loop = FeedbackLoop(
        observer=observer,
        analyzer=analyzer,
        adjustment_engine=adjuster,
        config=LoopConfig(
            analyze_every_n_ticks=10,
            auto_apply_adjustments=True,
            confidence_threshold=0.6,
            max_iterations=30,
            pause_on_concern=False,
        ),
    )

    def on_iteration(it):
        if it.iteration % 5 == 0 or it.analysis:
            m = it.snapshot.metrics
            status = f"[Tick {m['tick']:2d}] price={m['price']:6.2f} sentiment={m['sentiment']:.3f} vol={m['volume']}"
            if it.analysis:
                obs = it.analysis.observations[0] if it.analysis.observations else "No observations"
                status += f"\n  LLM: {obs}"
                if it.analysis.concerns:
                    status += f"\n  Concerns: {it.analysis.concerns}"
            print(status)

    loop.on_iteration = on_iteration

    print("Running...\n")

    try:
        loop.run(tick_callback=sim.step, tick_interval=0.05)
    except Exception as e:
        print(f"\nError: {e}")
        print("Run with --mock to skip LLM calls")

    print("\n" + "=" * 50)
    print("Summary:", loop.get_summary())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use mock analyzer (no LLM)")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    args = parser.parse_args()

    run(use_llm=not args.mock, seed=args.seed)
