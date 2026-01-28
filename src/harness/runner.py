"""
Autonomous Runner - Runs simulations continuously with AI-generated ideas.

This is the main entry point for autonomous testing. It:
1. Generates ideas using IdeaGenerator
2. Runs simulations via SimulationEngine
3. Tracks experiments via ExperimentTracker
4. Learns from results and adapts generation
"""

import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Any
from enum import Enum

from ..models.token import Token, MemeStyle, MarketCondition
from ..simulation.engine import SimulationEngine
from .idea_generator import IdeaGenerator, GeneratedIdea, IdeaStrategy
from .experiment import ExperimentTracker, Experiment, ExperimentStatus


class RunMode(str, Enum):
    """Different modes for autonomous running."""
    EXPLORE = "explore"         # Try diverse strategies, maximize learning
    EXPLOIT = "exploit"         # Focus on what's working
    BALANCED = "balanced"       # Mix of explore and exploit
    TARGETED = "targeted"       # Focus on specific strategy/theme


@dataclass
class RunConfig:
    """Configuration for an autonomous run."""
    mode: RunMode = RunMode.BALANCED
    max_experiments: int = 10
    simulation_hours: int = 24
    market_condition: MarketCondition = MarketCondition.CRAB

    # Strategy weights (for balanced/explore modes)
    strategy_weights: dict[str, float] = field(default_factory=lambda: {
        IdeaStrategy.TREND_CHASE.value: 0.25,
        IdeaStrategy.CONTRARIAN.value: 0.15,
        IdeaStrategy.REMIX.value: 0.20,
        IdeaStrategy.AVANT_GARDE.value: 0.15,
        IdeaStrategy.NOSTALGIA.value: 0.15,
        IdeaStrategy.TOPICAL.value: 0.10,
    })

    # For targeted mode
    target_strategy: Optional[IdeaStrategy] = None
    target_theme: Optional[str] = None

    # Callbacks
    on_experiment_start: Optional[Callable[[Experiment], None]] = None
    on_experiment_complete: Optional[Callable[[Experiment], None]] = None
    on_run_complete: Optional[Callable[[list[Experiment]], None]] = None
    on_simulation_progress: Optional[Callable[[str, int, int, dict], None]] = None  # exp_id, hour, total_hours, metrics

    # Behavior
    pause_between_experiments: float = 0.5  # seconds
    verbose: bool = True
    use_llm_generation: bool = True  # False uses template fallback
    adapt_weights: bool = True  # Adjust strategy weights based on results


@dataclass
class RunResult:
    """Results from an autonomous run."""
    experiments: list[Experiment]
    duration_seconds: float
    ideas_generated: int
    simulations_completed: int
    simulations_failed: int

    best_experiment: Optional[Experiment]
    avg_score: float

    learnings: list[str]
    adapted_weights: dict[str, float]


class AutonomousRunner:
    """Runs simulations autonomously with AI-generated ideas."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        experiments_dir: str = "./experiments",
    ):
        self.idea_generator = IdeaGenerator(api_key=api_key)
        self.simulation_engine = SimulationEngine(api_key=api_key)
        self.tracker = ExperimentTracker(storage_dir=experiments_dir)

        self._current_weights: dict[str, float] = {}
        self._run_history: list[RunResult] = []

    def run(self, config: RunConfig) -> RunResult:
        """
        Run an autonomous experiment session.

        Args:
            config: Configuration for this run
        """
        start_time = time.time()
        experiments: list[Experiment] = []

        # Initialize weights
        self._current_weights = config.strategy_weights.copy()

        if config.verbose:
            print(f"\n{'='*60}")
            print(f"AUTONOMOUS RUN - {config.mode.value.upper()} MODE")
            print(f"Max experiments: {config.max_experiments}")
            print(f"Market condition: {config.market_condition.value}")
            print(f"{'='*60}\n")

        for i in range(config.max_experiments):
            if config.verbose:
                print(f"\n[{i+1}/{config.max_experiments}] Generating idea...")

            # Generate idea based on mode
            idea = self._generate_idea(config)

            if not idea:
                if config.verbose:
                    print("  Failed to generate idea, skipping...")
                continue

            # Create experiment
            experiment = self.tracker.create_experiment(idea)

            if config.verbose:
                print(f"  Created: {idea.name} (${idea.ticker})")
                print(f"  Strategy: {idea.strategy.value}")
                print(f"  Hook: {idea.hook[:60]}..." if len(idea.hook) > 60 else f"  Hook: {idea.hook}")

            if config.on_experiment_start:
                config.on_experiment_start(experiment)

            # Run simulation
            experiment.start()
            self.tracker.update_experiment(experiment)

            try:
                if config.verbose:
                    print(f"  Running simulation ({config.simulation_hours}h)...")

                # Convert idea to Token
                token = Token(
                    name=idea.name,
                    ticker=idea.ticker,
                    narrative=idea.narrative,
                    tagline=idea.tagline,
                    meme_style=idea.meme_style,
                    market_condition=config.market_condition,
                )

                # Use streaming simulation if progress callback is set
                if config.on_simulation_progress:
                    result_dict = None
                    for event in self.simulation_engine.run_simulation_stream(
                        token=token,
                        hours=config.simulation_hours,
                    ):
                        if event["type"] == "progress":
                            config.on_simulation_progress(
                                experiment.id,
                                event["hour"],
                                event["total_hours"],
                                {
                                    "momentum": event.get("momentum", 0),
                                    "awareness": event.get("awareness", 0),
                                    "tweet_count": event.get("tweet_count", 0),
                                    "sentiment": event.get("sentiment", 0),
                                }
                            )
                        elif event["type"] == "result":
                            result_dict = event["result"]

                    if result_dict is None:
                        raise Exception("Simulation did not return result")

                    # Convert dict to SimulationResult
                    from ..models.token import SimulationResult
                    result_dict["token"] = token.model_dump()
                    result = SimulationResult.model_validate(result_dict)
                else:
                    result = self.simulation_engine.run_simulation(
                        token=token,
                        hours=config.simulation_hours,
                        verbose=False,
                    )

                experiment.complete(result)
                self.tracker.update_experiment(experiment)

                if config.verbose:
                    print(f"  Score: {experiment.score:.2%}")
                    print(f"  Outcome: {result.predicted_outcome}")
                    print(f"  Viral coefficient: {result.viral_coefficient:.2f}x")

            except Exception as e:
                experiment.fail(str(e))
                self.tracker.update_experiment(experiment)
                if config.verbose:
                    print(f"  FAILED: {e}")

            experiments.append(experiment)

            if config.on_experiment_complete:
                config.on_experiment_complete(experiment)

            # Adapt weights if enabled
            if config.adapt_weights and experiment.status == ExperimentStatus.COMPLETED:
                self._adapt_weights(experiment)

            # Pause between experiments
            if config.pause_between_experiments > 0 and i < config.max_experiments - 1:
                time.sleep(config.pause_between_experiments)

        # Compile results
        duration = time.time() - start_time
        completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
        failed = [e for e in experiments if e.status == ExperimentStatus.FAILED]

        scores = [e.score for e in completed if e.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        best = max(completed, key=lambda e: e.score or 0) if completed else None

        # Generate learnings
        learnings = self._extract_learnings(experiments)

        result = RunResult(
            experiments=experiments,
            duration_seconds=duration,
            ideas_generated=len(experiments),
            simulations_completed=len(completed),
            simulations_failed=len(failed),
            best_experiment=best,
            avg_score=avg_score,
            learnings=learnings,
            adapted_weights=self._current_weights.copy(),
        )

        self._run_history.append(result)

        if config.on_run_complete:
            config.on_run_complete(experiments)

        if config.verbose:
            self._print_summary(result)

        return result

    def run_single(
        self,
        idea: GeneratedIdea,
        simulation_hours: int = 24,
        market_condition: MarketCondition = MarketCondition.CRAB,
        verbose: bool = True,
    ) -> Experiment:
        """Run a single experiment with a provided idea."""
        experiment = self.tracker.create_experiment(idea)
        experiment.start()

        try:
            token = Token(
                name=idea.name,
                ticker=idea.ticker,
                narrative=idea.narrative,
                tagline=idea.tagline,
                meme_style=idea.meme_style,
                market_condition=market_condition,
            )

            result = self.simulation_engine.run_simulation(
                token=token,
                hours=simulation_hours,
                verbose=verbose,
            )

            experiment.complete(result)

        except Exception as e:
            experiment.fail(str(e))

        self.tracker.update_experiment(experiment)
        return experiment

    def brainstorm_and_test(
        self,
        theme: str,
        num_ideas: int = 5,
        simulation_hours: int = 24,
        market_condition: MarketCondition = MarketCondition.CRAB,
        verbose: bool = True,
    ) -> list[Experiment]:
        """Brainstorm ideas around a theme and test them all."""
        if verbose:
            print(f"\nBrainstorming {num_ideas} ideas around: '{theme}'")

        ideas = self.idea_generator.brainstorm(theme, num_ideas)

        if verbose:
            print(f"Generated {len(ideas)} ideas:")
            for idea in ideas:
                print(f"  - {idea.name} (${idea.ticker})")

        experiments = []
        for i, idea in enumerate(ideas):
            if verbose:
                print(f"\n[{i+1}/{len(ideas)}] Testing: {idea.name}")

            exp = self.run_single(
                idea=idea,
                simulation_hours=simulation_hours,
                market_condition=market_condition,
                verbose=False,
            )
            experiments.append(exp)

            if verbose and exp.status == ExperimentStatus.COMPLETED:
                print(f"  Score: {exp.score:.2%}")
                print(f"  Outcome: {exp.result.predicted_outcome if exp.result else 'N/A'}")

        # Rank results
        if verbose and experiments:
            completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
            ranked = sorted(completed, key=lambda e: e.score or 0, reverse=True)
            print(f"\n{'='*40}")
            print("RANKING")
            print(f"{'='*40}")
            for i, exp in enumerate(ranked, 1):
                print(f"{i}. {exp.idea.name} - {exp.score:.2%}")

        return experiments

    def _generate_idea(self, config: RunConfig) -> Optional[GeneratedIdea]:
        """Generate an idea based on run configuration."""
        try:
            if config.mode == RunMode.TARGETED:
                if config.target_theme:
                    ideas = self.idea_generator.brainstorm(config.target_theme, 1)
                else:
                    ideas = self.idea_generator.generate(
                        strategy=config.target_strategy,
                        market_condition=config.market_condition,
                        num_ideas=1,
                    )
            elif config.mode == RunMode.EXPLOIT:
                # Focus on best-performing strategy
                best_strategy = self._get_best_strategy()
                ideas = self.idea_generator.generate(
                    strategy=best_strategy,
                    market_condition=config.market_condition,
                    num_ideas=1,
                )
            else:
                # Explore or Balanced: weighted random
                strategy = self._select_strategy_weighted()
                ideas = self.idea_generator.generate(
                    strategy=strategy,
                    market_condition=config.market_condition,
                    num_ideas=1,
                )

            return ideas[0] if ideas else None

        except Exception as e:
            return None

    def _select_strategy_weighted(self) -> IdeaStrategy:
        """Select a strategy based on current weights."""
        strategies = list(IdeaStrategy)
        weights = [self._current_weights.get(s.value, 0.1) for s in strategies]

        # Normalize
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(strategies, weights=weights)[0]

    def _get_best_strategy(self) -> IdeaStrategy:
        """Get the best performing strategy from history."""
        summary = self.tracker.get_summary()
        if summary.strategy_performance:
            best = max(summary.strategy_performance.items(), key=lambda x: x[1])
            return IdeaStrategy(best[0])
        return random.choice(list(IdeaStrategy))

    def _adapt_weights(self, experiment: Experiment):
        """Adapt strategy weights based on experiment results."""
        if experiment.score is None:
            return

        strategy = experiment.idea.strategy.value

        # Adjust weight based on score
        if experiment.score > 0.6:
            # Increase weight for successful strategy
            self._current_weights[strategy] = min(0.4, self._current_weights.get(strategy, 0.1) * 1.2)
        elif experiment.score < 0.3:
            # Decrease weight for poor strategy
            self._current_weights[strategy] = max(0.05, self._current_weights.get(strategy, 0.1) * 0.8)

        # Normalize weights
        total = sum(self._current_weights.values())
        self._current_weights = {k: v / total for k, v in self._current_weights.items()}

    def _extract_learnings(self, experiments: list[Experiment]) -> list[str]:
        """Extract learnings from a batch of experiments."""
        learnings = []

        completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
        if not completed:
            return ["No completed experiments to learn from"]

        # Best performer
        best = max(completed, key=lambda e: e.score or 0)
        learnings.append(f"Best performer: {best.idea.name} ({best.score:.2%}) - {best.idea.strategy.value}")

        # Strategy analysis
        strategy_scores: dict[str, list[float]] = {}
        for exp in completed:
            strat = exp.idea.strategy.value
            if strat not in strategy_scores:
                strategy_scores[strat] = []
            if exp.score:
                strategy_scores[strat].append(exp.score)

        for strat, scores in strategy_scores.items():
            avg = sum(scores) / len(scores)
            learnings.append(f"Strategy '{strat}': {avg:.2%} avg score ({len(scores)} experiments)")

        # Common patterns in top performers
        top_half = sorted(completed, key=lambda e: e.score or 0, reverse=True)[:len(completed)//2]
        if top_half:
            styles = {}
            for exp in top_half:
                style = exp.idea.meme_style.value
                styles[style] = styles.get(style, 0) + 1
            if styles:
                top_style = max(styles.items(), key=lambda x: x[1])
                learnings.append(f"Top performers favor '{top_style[0]}' meme style")

        return learnings

    def _print_summary(self, result: RunResult):
        """Print a summary of the run."""
        print(f"\n{'='*60}")
        print("RUN COMPLETE")
        print(f"{'='*60}")
        print(f"Duration: {result.duration_seconds:.1f}s")
        print(f"Experiments: {result.simulations_completed} completed, {result.simulations_failed} failed")
        print(f"Average score: {result.avg_score:.2%}")

        if result.best_experiment:
            print(f"\nBest: {result.best_experiment.idea.name} (${result.best_experiment.idea.ticker})")
            print(f"  Score: {result.best_experiment.score:.2%}")
            print(f"  Hook: {result.best_experiment.idea.hook}")

        print("\nLearnings:")
        for learning in result.learnings:
            print(f"  • {learning}")

        print("\nAdapted weights:")
        for strat, weight in sorted(result.adapted_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  {strat}: {weight:.2%}")
