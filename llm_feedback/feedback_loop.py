"""
Feedback Loop Module

Orchestrates the observe -> analyze -> adjust cycle on SYNTHETIC simulations.
No real-time data - purely synthetic/generated environments.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime
import time
import json

from .observer import SimulationObserver, StateSnapshot
from .analyzer import LLMAnalyzer, Analysis
from .adjustments import AdjustmentEngine


@dataclass
class LoopIteration:
    """Record of one feedback loop iteration."""
    iteration: int
    timestamp: datetime
    snapshot: StateSnapshot
    analysis: Optional[Analysis]
    adjustments_made: list[tuple[str, bool, str]]
    duration_ms: float


@dataclass
class LoopConfig:
    """Configuration for feedback loop behavior."""
    analyze_every_n_ticks: int = 5
    auto_apply_adjustments: bool = False
    confidence_threshold: float = 0.7
    max_iterations: Optional[int] = None
    pause_on_concern: bool = True
    log_to_file: Optional[str] = None


class FeedbackLoop:
    """
    Orchestrates the LLM feedback loop on SYNTHETIC simulations.

    This is for testing/iteration on generated data only.
    Real data should only inform priors, not be monitored live.
    """

    def __init__(
        self,
        observer: SimulationObserver,
        analyzer: LLMAnalyzer,
        adjustment_engine: Optional[AdjustmentEngine] = None,
        config: Optional[LoopConfig] = None,
    ):
        self.observer = observer
        self.analyzer = analyzer
        self.adjustment_engine = adjustment_engine
        self.config = config or LoopConfig()

        self.iterations: list[LoopIteration] = []
        self.is_running = False
        self.is_paused = False
        self.current_iteration = 0

        self.on_iteration: Optional[Callable[[LoopIteration], None]] = None
        self.on_analysis: Optional[Callable[[Analysis], None]] = None
        self.on_pause: Optional[Callable[[str], None]] = None

    def tick(self) -> LoopIteration:
        """Execute one iteration of the feedback loop."""
        start_time = time.time()
        self.current_iteration += 1

        snapshot = self.observer.observe()

        analysis = None
        adjustments = []

        should_analyze = (self.current_iteration % self.config.analyze_every_n_ticks == 0)

        if should_analyze:
            context = self.observer.get_full_context()
            analysis = self.analyzer.analyze(context)

            if self.on_analysis:
                self.on_analysis(analysis)

            if self.config.pause_on_concern and analysis.concerns:
                self.is_paused = True
                if self.on_pause:
                    self.on_pause(f"Concerns detected: {analysis.concerns}")

            if (self.config.auto_apply_adjustments
                and self.adjustment_engine
                and analysis.has_recommendations()
                and analysis.confidence >= self.config.confidence_threshold):

                adjustments = self.adjustment_engine.apply_recommendations(
                    analysis.recommendations,
                    self.config.confidence_threshold,
                    analysis.confidence,
                )

        duration_ms = (time.time() - start_time) * 1000

        iteration = LoopIteration(
            iteration=self.current_iteration,
            timestamp=datetime.now(),
            snapshot=snapshot,
            analysis=analysis,
            adjustments_made=adjustments,
            duration_ms=duration_ms,
        )

        self.iterations.append(iteration)

        if self.on_iteration:
            self.on_iteration(iteration)

        if self.config.log_to_file:
            self._log_iteration(iteration)

        return iteration

    def run(
        self,
        tick_callback: Callable[[], bool],
        tick_interval: float = 1.0,
    ):
        """Run the feedback loop continuously."""
        self.is_running = True

        while self.is_running:
            if self.config.max_iterations and self.current_iteration >= self.config.max_iterations:
                break

            if self.is_paused:
                time.sleep(0.1)
                continue

            should_continue = tick_callback()
            if not should_continue:
                break

            self.tick()
            time.sleep(tick_interval)

        self.is_running = False

    def force_analysis(self) -> Analysis:
        """Force an immediate analysis."""
        context = self.observer.get_full_context()
        return self.analyzer.analyze(context)

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_running = False

    def get_summary(self) -> dict[str, Any]:
        analyses = [i.analysis for i in self.iterations if i.analysis]
        all_adjustments = [a for i in self.iterations for a in i.adjustments_made]

        return {
            "total_iterations": self.current_iteration,
            "analyses_performed": len(analyses),
            "adjustments_made": len([a for a in all_adjustments if a[1]]),
            "adjustments_rejected": len([a for a in all_adjustments if not a[1]]),
            "avg_confidence": (
                sum(a.confidence for a in analyses) / len(analyses)
                if analyses else 0
            ),
            "concerns_raised": sum(len(a.concerns) for a in analyses),
        }

    def _log_iteration(self, iteration: LoopIteration):
        log_entry = {
            "iteration": iteration.iteration,
            "timestamp": iteration.timestamp.isoformat(),
            "metrics": iteration.snapshot.metrics,
            "duration_ms": iteration.duration_ms,
        }
        if iteration.analysis:
            log_entry["analysis"] = iteration.analysis.to_dict()

        with open(self.config.log_to_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
