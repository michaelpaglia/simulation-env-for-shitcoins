"""
Experiment Tracking - Track and analyze autonomous simulation experiments.

Maintains a history of:
- Generated ideas and their performance
- Successful patterns and failures
- Learnings that can inform future generation
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from enum import Enum

from ..models.token import SimulationResult, Token, MemeStyle, MarketCondition
from .idea_generator import GeneratedIdea, IdeaStrategy


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Experiment:
    """A single experiment - one idea + its simulation results."""
    id: str
    idea: GeneratedIdea
    status: ExperimentStatus = ExperimentStatus.PENDING
    result: Optional[SimulationResult] = None

    # Timing
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Analysis
    score: Optional[float] = None  # Composite score for ranking
    learnings: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def start(self):
        """Mark experiment as started."""
        self.status = ExperimentStatus.RUNNING
        self.started_at = datetime.now().isoformat()

    def complete(self, result: SimulationResult):
        """Mark experiment as completed with results."""
        self.status = ExperimentStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now().isoformat()
        self.score = self._calculate_score(result)

    def fail(self, error: str):
        """Mark experiment as failed."""
        self.status = ExperimentStatus.FAILED
        self.completed_at = datetime.now().isoformat()
        self.learnings.append(f"Failed: {error}")

    def _calculate_score(self, result: SimulationResult) -> float:
        """Calculate composite score for ranking experiments."""
        # Weighted combination of key metrics
        viral_weight = 0.25
        sentiment_weight = 0.20
        stability_weight = 0.15
        fud_resistance_weight = 0.15
        engagement_weight = 0.15
        outcome_weight = 0.10

        # Normalize viral coefficient (assuming 5x is excellent, use log scale)
        import math
        normalized_viral = min(1.0, math.log1p(result.viral_coefficient) / math.log1p(5))

        # Normalize engagement (assuming 50k is excellent)
        normalized_engagement = min(1.0, result.total_engagement / 50000)

        # Outcome score
        outcome_scores = {
            "moon": 1.0,
            "cult_classic": 0.8,
            "pump_and_dump": 0.4,
            "slow_bleed": 0.2,
            "rug": 0.0,
        }
        outcome_score = outcome_scores.get(result.predicted_outcome, 0.3)

        score = (
            normalized_viral * viral_weight +
            ((result.peak_sentiment + 1) / 2) * sentiment_weight +  # Normalize -1,1 to 0,1
            result.sentiment_stability * stability_weight +
            result.fud_resistance * fud_resistance_weight +
            normalized_engagement * engagement_weight +
            outcome_score * outcome_weight
        )

        # Confidence modifier (slight adjustment based on prediction confidence)
        score *= (0.9 + result.confidence * 0.1)

        return min(1.0, max(0.0, score))

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "idea": {
                "name": self.idea.name,
                "ticker": self.idea.ticker,
                "narrative": self.idea.narrative,
                "tagline": self.idea.tagline,
                "meme_style": self.idea.meme_style.value,
                "hook": self.idea.hook,
                "target_audience": self.idea.target_audience,
                "strategy": self.idea.strategy.value,
                "reasoning": self.idea.reasoning,
                "risk_factors": self.idea.risk_factors,
                "confidence": self.idea.confidence,
            },
            "status": self.status.value,
            "result": self.result.model_dump() if self.result else None,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "score": self.score,
            "learnings": self.learnings,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Experiment":
        """Create from dictionary."""
        idea_data = data["idea"]
        idea = GeneratedIdea(
            name=idea_data["name"],
            ticker=idea_data["ticker"],
            narrative=idea_data["narrative"],
            tagline=idea_data.get("tagline", ""),
            meme_style=MemeStyle(idea_data.get("meme_style", "absurd")),
            hook=idea_data.get("hook", ""),
            target_audience=idea_data.get("target_audience", "degens"),
            strategy=IdeaStrategy(idea_data.get("strategy", "trend_chase")),
            reasoning=idea_data.get("reasoning", ""),
            risk_factors=idea_data.get("risk_factors", []),
            confidence=idea_data.get("confidence", 0.5),
        )

        result = None
        if data.get("result"):
            result = SimulationResult.model_validate(data["result"])

        return cls(
            id=data["id"],
            idea=idea,
            status=ExperimentStatus(data.get("status", "pending")),
            result=result,
            created_at=data.get("created_at", datetime.now().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            score=data.get("score"),
            learnings=data.get("learnings", []),
            tags=data.get("tags", []),
        )


@dataclass
class ExperimentSummary:
    """Summary statistics across experiments."""
    total_experiments: int
    completed: int
    failed: int
    pending: int

    avg_score: float
    top_score: float
    top_experiment_id: Optional[str]

    # Strategy breakdown
    strategy_performance: dict[str, float]  # strategy -> avg score

    # Meme style breakdown
    style_performance: dict[str, float]  # style -> avg score

    # Outcome distribution
    outcome_distribution: dict[str, int]  # outcome -> count


class ExperimentTracker:
    """Tracks experiments and provides analytics."""

    def __init__(self, storage_dir: str = "./experiments"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.experiments: dict[str, Experiment] = {}
        self._load_experiments()
        self._next_id = len(self.experiments) + 1

    def _load_experiments(self):
        """Load experiments from storage."""
        index_file = self.storage_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    data = json.load(f)
                    for exp_data in data.get("experiments", []):
                        exp = Experiment.from_dict(exp_data)
                        self.experiments[exp.id] = exp
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_experiments(self):
        """Save experiments to storage."""
        index_file = self.storage_dir / "index.json"
        data = {
            "experiments": [exp.to_dict() for exp in self.experiments.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(index_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create_experiment(self, idea: GeneratedIdea) -> Experiment:
        """Create a new experiment from an idea."""
        exp_id = f"exp_{self._next_id:04d}"
        self._next_id += 1

        experiment = Experiment(id=exp_id, idea=idea)
        self.experiments[exp_id] = experiment
        self._save_experiments()

        return experiment

    def get_experiment(self, exp_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        return self.experiments.get(exp_id)

    def update_experiment(self, experiment: Experiment):
        """Update an experiment."""
        self.experiments[experiment.id] = experiment
        self._save_experiments()

    def get_all(
        self,
        status: Optional[ExperimentStatus] = None,
        strategy: Optional[IdeaStrategy] = None,
        min_score: Optional[float] = None,
    ) -> list[Experiment]:
        """Get experiments with optional filters."""
        experiments = list(self.experiments.values())

        if status:
            experiments = [e for e in experiments if e.status == status]

        if strategy:
            experiments = [e for e in experiments if e.idea.strategy == strategy]

        if min_score is not None:
            experiments = [e for e in experiments if e.score and e.score >= min_score]

        return experiments

    def get_top_performers(self, n: int = 10) -> list[Experiment]:
        """Get top N performing experiments."""
        completed = [e for e in self.experiments.values()
                     if e.status == ExperimentStatus.COMPLETED and e.score is not None]
        return sorted(completed, key=lambda e: e.score or 0, reverse=True)[:n]

    def get_summary(self) -> ExperimentSummary:
        """Get summary statistics across all experiments."""
        experiments = list(self.experiments.values())

        completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
        failed = [e for e in experiments if e.status == ExperimentStatus.FAILED]
        pending = [e for e in experiments if e.status == ExperimentStatus.PENDING]

        # Calculate averages
        scores = [e.score for e in completed if e.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        top_score = max(scores) if scores else 0

        top_exp = max(completed, key=lambda e: e.score or 0) if completed else None

        # Strategy performance
        strategy_scores: dict[str, list[float]] = {}
        for exp in completed:
            strat = exp.idea.strategy.value
            if strat not in strategy_scores:
                strategy_scores[strat] = []
            if exp.score is not None:
                strategy_scores[strat].append(exp.score)

        strategy_performance = {
            strat: sum(scores) / len(scores)
            for strat, scores in strategy_scores.items() if scores
        }

        # Style performance
        style_scores: dict[str, list[float]] = {}
        for exp in completed:
            style = exp.idea.meme_style.value
            if style not in style_scores:
                style_scores[style] = []
            if exp.score is not None:
                style_scores[style].append(exp.score)

        style_performance = {
            style: sum(scores) / len(scores)
            for style, scores in style_scores.items() if scores
        }

        # Outcome distribution
        outcome_distribution: dict[str, int] = {}
        for exp in completed:
            if exp.result:
                outcome = exp.result.predicted_outcome
                outcome_distribution[outcome] = outcome_distribution.get(outcome, 0) + 1

        return ExperimentSummary(
            total_experiments=len(experiments),
            completed=len(completed),
            failed=len(failed),
            pending=len(pending),
            avg_score=avg_score,
            top_score=top_score,
            top_experiment_id=top_exp.id if top_exp else None,
            strategy_performance=strategy_performance,
            style_performance=style_performance,
            outcome_distribution=outcome_distribution,
        )

    def get_learnings(self) -> dict[str, Any]:
        """Extract learnings from completed experiments."""
        completed = [e for e in self.experiments.values()
                     if e.status == ExperimentStatus.COMPLETED and e.score is not None]

        if not completed:
            return {"message": "No completed experiments yet"}

        # Find patterns in successful experiments
        successful = [e for e in completed if (e.score or 0) >= 0.6]
        unsuccessful = [e for e in completed if (e.score or 0) < 0.4]

        learnings = {
            "total_analyzed": len(completed),
            "success_rate": len(successful) / len(completed) if completed else 0,

            "winning_patterns": {
                "strategies": self._count_field(successful, lambda e: e.idea.strategy.value),
                "styles": self._count_field(successful, lambda e: e.idea.meme_style.value),
                "audiences": self._count_field(successful, lambda e: e.idea.target_audience),
            },

            "losing_patterns": {
                "strategies": self._count_field(unsuccessful, lambda e: e.idea.strategy.value),
                "styles": self._count_field(unsuccessful, lambda e: e.idea.meme_style.value),
                "audiences": self._count_field(unsuccessful, lambda e: e.idea.target_audience),
            },

            "insights": self._generate_insights(successful, unsuccessful),
        }

        return learnings

    def _count_field(self, experiments: list[Experiment], field_fn) -> dict[str, int]:
        """Count occurrences of a field value."""
        counts: dict[str, int] = {}
        for exp in experiments:
            value = field_fn(exp)
            counts[value] = counts.get(value, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _generate_insights(
        self,
        successful: list[Experiment],
        unsuccessful: list[Experiment],
    ) -> list[str]:
        """Generate insights from experiment data."""
        insights = []

        if not successful and not unsuccessful:
            return ["Not enough data for insights"]

        # Strategy insights
        if successful:
            strat_counts = self._count_field(successful, lambda e: e.idea.strategy.value)
            if strat_counts:
                top_strat = list(strat_counts.keys())[0]
                insights.append(f"Most successful strategy: {top_strat}")

        # Style insights
        if successful:
            style_counts = self._count_field(successful, lambda e: e.idea.meme_style.value)
            if style_counts:
                top_style = list(style_counts.keys())[0]
                insights.append(f"Most successful meme style: {top_style}")

        # Risk factor analysis
        common_risks = {}
        for exp in unsuccessful:
            for risk in exp.idea.risk_factors:
                common_risks[risk] = common_risks.get(risk, 0) + 1

        if common_risks:
            top_risks = sorted(common_risks.items(), key=lambda x: x[1], reverse=True)[:3]
            for risk, count in top_risks:
                insights.append(f"Common failure risk: '{risk}' ({count} occurrences)")

        return insights

    def export_report(self, filepath: Optional[str] = None) -> str:
        """Export a full report of experiments."""
        summary = self.get_summary()
        learnings = self.get_learnings()
        top_performers = self.get_top_performers(5)

        report = f"""
================================================================================
EXPERIMENT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

SUMMARY
-------
Total Experiments: {summary.total_experiments}
Completed: {summary.completed} | Failed: {summary.failed} | Pending: {summary.pending}

Average Score: {summary.avg_score:.2%}
Top Score: {summary.top_score:.2%} (Experiment: {summary.top_experiment_id})

STRATEGY PERFORMANCE
--------------------
"""
        for strat, score in sorted(summary.strategy_performance.items(), key=lambda x: x[1], reverse=True):
            report += f"  {strat}: {score:.2%}\n"

        report += """
STYLE PERFORMANCE
-----------------
"""
        for style, score in sorted(summary.style_performance.items(), key=lambda x: x[1], reverse=True):
            report += f"  {style}: {score:.2%}\n"

        report += """
OUTCOME DISTRIBUTION
--------------------
"""
        for outcome, count in sorted(summary.outcome_distribution.items(), key=lambda x: x[1], reverse=True):
            report += f"  {outcome}: {count}\n"

        report += """
TOP PERFORMERS
--------------
"""
        for i, exp in enumerate(top_performers, 1):
            report += f"""
{i}. {exp.idea.name} (${exp.idea.ticker})
   Score: {exp.score:.2%}
   Strategy: {exp.idea.strategy.value}
   Hook: {exp.idea.hook}
   Outcome: {exp.result.predicted_outcome if exp.result else 'N/A'}
"""

        report += """
LEARNINGS
---------
"""
        for insight in learnings.get("insights", []):
            report += f"  • {insight}\n"

        if filepath:
            with open(filepath, "w") as f:
                f.write(report)

        return report
