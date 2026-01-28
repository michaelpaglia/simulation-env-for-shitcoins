"""
Observer Module

Captures and structures SYNTHETIC simulation state for LLM analysis.
No real-time/live data - purely observes generated simulation state.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime
import json


@dataclass
class StateSnapshot:
    """A point-in-time capture of synthetic simulation state."""
    timestamp: datetime
    tick: int
    metrics: dict[str, Any]
    events: list[dict[str, Any]]
    raw_state: dict[str, Any]

    def to_prompt_context(self) -> str:
        """Format snapshot for LLM consumption."""
        return json.dumps({
            "tick": self.tick,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "recent_events": self.events[-10:] if self.events else [],
        }, indent=2)


@dataclass
class ObservationHistory:
    """Maintains history of observations for trend analysis."""
    snapshots: list[StateSnapshot] = field(default_factory=list)
    max_history: int = 100

    def add(self, snapshot: StateSnapshot):
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_history:
            self.snapshots = self.snapshots[-self.max_history:]

    def get_trend_context(self, window: int = 5) -> str:
        """Get recent snapshots formatted for trend analysis."""
        recent = self.snapshots[-window:] if self.snapshots else []
        return json.dumps([{
            "tick": s.tick,
            "metrics": s.metrics
        } for s in recent], indent=2)


class SimulationObserver:
    """
    Observes a running SYNTHETIC simulation and captures state snapshots.

    This does NOT connect to live/real data sources. It observes
    generated simulation state only.
    """

    def __init__(
        self,
        state_extractor: Callable[[], dict[str, Any]],
        metrics_extractor: Callable[[], dict[str, Any]],
        events_extractor: Optional[Callable[[], list[dict]]] = None,
    ):
        """
        Args:
            state_extractor: Function returning current synthetic state
            metrics_extractor: Function returning current synthetic metrics
            events_extractor: Optional function returning recent synthetic events
        """
        self.state_extractor = state_extractor
        self.metrics_extractor = metrics_extractor
        self.events_extractor = events_extractor or (lambda: [])
        self.history = ObservationHistory()
        self.tick_count = 0

    def observe(self) -> StateSnapshot:
        """Capture current simulation state."""
        snapshot = StateSnapshot(
            timestamp=datetime.now(),
            tick=self.tick_count,
            metrics=self.metrics_extractor(),
            events=self.events_extractor(),
            raw_state=self.state_extractor(),
        )
        self.history.add(snapshot)
        self.tick_count += 1
        return snapshot

    def get_full_context(self) -> str:
        """Get full context string for LLM analysis."""
        if not self.history.snapshots:
            return "No observations yet."

        latest = self.history.snapshots[-1]
        return f"""## Current State (Tick {latest.tick})
{latest.to_prompt_context()}

## Recent Trend (Last 5 ticks)
{self.history.get_trend_context()}

## Total Observations: {len(self.history.snapshots)}
"""

    def reset(self):
        """Reset observation history."""
        self.history = ObservationHistory()
        self.tick_count = 0
