"""Harness API routes for autonomous experiment runs."""

import os
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from enum import Enum
import threading
from queue import Queue
from datetime import datetime

from ..models.token import MarketCondition
from ..harness.runner import AutonomousRunner, RunConfig, RunMode
from ..harness.idea_generator import IdeaStrategy
from ..harness.experiment import ExperimentTracker, ExperimentStatus

router = APIRouter(prefix="/harness", tags=["harness"])

# Global state for the running harness
_harness_state = {
    "is_running": False,
    "run_id": None,
    "current_experiment": None,
    "events_queue": None,
    "events_list": [],  # Broadcast list - stores recent events
    "events_counter": 0,  # Counter for event IDs
    "runner": None,
    "thread": None,
}


class RunModeEnum(str, Enum):
    balanced = "balanced"
    explore = "explore"
    exploit = "exploit"
    targeted = "targeted"


class HarnessRunRequest(BaseModel):
    mode: RunModeEnum = RunModeEnum.balanced
    max_experiments: int = Field(default=5, ge=1, le=50)
    simulation_hours: int = Field(default=24, ge=6, le=48)
    market_condition: str = Field(default="crab")
    target_theme: Optional[str] = None


class HarnessRunResponse(BaseModel):
    run_id: str
    status: str


class HarnessStatusResponse(BaseModel):
    is_running: bool
    run_id: Optional[str]
    current_experiment: Optional[str]
    progress: Optional[dict]
    elapsed_seconds: Optional[float]


def _emit_event(event: dict):
    """Emit an event to all connected SSE clients."""
    # Add to broadcast list with an ID
    event["_id"] = _harness_state["events_counter"]
    _harness_state["events_counter"] += 1
    _harness_state["events_list"].append(event)
    # Keep only last 100 events to prevent memory issues
    if len(_harness_state["events_list"]) > 100:
        _harness_state["events_list"] = _harness_state["events_list"][-100:]
    # Also add to queue for backwards compatibility
    if _harness_state["events_queue"]:
        _harness_state["events_queue"].put(event)


def _run_harness_thread(config: RunConfig, run_id: str):
    """Run the harness in a background thread."""
    global _harness_state

    try:
        runner = AutonomousRunner(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            experiments_dir="./experiments",
        )
        _harness_state["runner"] = runner

        # Emit run started
        _emit_event({
            "type": "run_started",
            "run_id": run_id,
            "config": {
                "mode": config.mode.value,
                "max_experiments": config.max_experiments,
                "simulation_hours": config.simulation_hours,
                "market_condition": config.market_condition.value,
            },
            "timestamp": datetime.now().isoformat(),
        })

        # Override callbacks to emit events
        original_config = config
        experiments_completed = 0

        def on_experiment_start(exp):
            nonlocal experiments_completed
            _harness_state["current_experiment"] = exp.id
            _emit_event({
                "type": "experiment_started",
                "experiment_id": exp.id,
                "experiment_index": experiments_completed + 1,
                "total_experiments": original_config.max_experiments,
                "idea": {
                    "name": exp.idea.name,
                    "ticker": exp.idea.ticker,
                    "narrative": exp.idea.narrative,
                    "tagline": exp.idea.tagline,
                    "hook": exp.idea.hook,
                    "strategy": exp.idea.strategy.value,
                    "meme_style": exp.idea.meme_style.value,
                    "confidence": exp.idea.confidence,
                },
                "timestamp": datetime.now().isoformat(),
            })

        def on_experiment_complete(exp):
            nonlocal experiments_completed
            experiments_completed += 1
            _emit_event({
                "type": "experiment_completed",
                "experiment_id": exp.id,
                "experiment_index": experiments_completed,
                "total_experiments": original_config.max_experiments,
                "idea": {
                    "name": exp.idea.name,
                    "ticker": exp.idea.ticker,
                    "hook": exp.idea.hook,
                    "strategy": exp.idea.strategy.value,
                    "meme_style": exp.idea.meme_style.value,
                },
                "status": exp.status.value,
                "score": exp.score,
                "result": {
                    "predicted_outcome": exp.result.predicted_outcome if exp.result else None,
                    "viral_coefficient": exp.result.viral_coefficient if exp.result else None,
                    "peak_sentiment": exp.result.peak_sentiment if exp.result else None,
                    "fud_resistance": exp.result.fud_resistance if exp.result else None,
                    "total_engagement": exp.result.total_engagement if exp.result else None,
                    "dominant_narrative": exp.result.dominant_narrative if exp.result else None,
                } if exp.result else None,
                "timestamp": datetime.now().isoformat(),
            })

        def on_run_complete(experiments):
            completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
            scores = [e.score for e in completed if e.score is not None]
            best = max(completed, key=lambda e: e.score or 0) if completed else None

            _emit_event({
                "type": "run_completed",
                "run_id": run_id,
                "summary": {
                    "total_experiments": len(experiments),
                    "completed": len(completed),
                    "failed": len([e for e in experiments if e.status == ExperimentStatus.FAILED]),
                    "avg_score": sum(scores) / len(scores) if scores else 0,
                    "best_experiment": {
                        "id": best.id,
                        "ticker": best.idea.ticker,
                        "name": best.idea.name,
                        "score": best.score,
                    } if best else None,
                },
                "timestamp": datetime.now().isoformat(),
            })

        def on_simulation_progress(exp_id, hour, total_hours, metrics):
            _emit_event({
                "type": "simulation_progress",
                "experiment_id": exp_id,
                "hour": hour,
                "total_hours": total_hours,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            })

        config.on_experiment_start = on_experiment_start
        config.on_experiment_complete = on_experiment_complete
        config.on_run_complete = on_run_complete
        config.on_simulation_progress = on_simulation_progress
        config.verbose = False

        # Run the harness
        runner.run(config)

    except Exception as e:
        _emit_event({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        })
    finally:
        _harness_state["is_running"] = False
        _harness_state["current_experiment"] = None
        _emit_event({"type": "done"})


@router.post("/run", response_model=HarnessRunResponse)
async def start_harness_run(request: HarnessRunRequest):
    """Start an autonomous harness run."""
    global _harness_state

    if _harness_state["is_running"]:
        raise HTTPException(status_code=409, detail="Harness is already running")

    # Map request to RunConfig
    mode_map = {
        RunModeEnum.balanced: RunMode.BALANCED,
        RunModeEnum.explore: RunMode.EXPLORE,
        RunModeEnum.exploit: RunMode.EXPLOIT,
        RunModeEnum.targeted: RunMode.TARGETED,
    }

    market_map = {
        "bear": MarketCondition.BEAR,
        "crab": MarketCondition.CRAB,
        "bull": MarketCondition.BULL,
        "euphoria": MarketCondition.EUPHORIA,
    }

    config = RunConfig(
        mode=mode_map[request.mode],
        max_experiments=request.max_experiments,
        simulation_hours=request.simulation_hours,
        market_condition=market_map.get(request.market_condition, MarketCondition.CRAB),
        target_theme=request.target_theme,
    )

    # Generate run ID
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Setup state
    _harness_state["is_running"] = True
    _harness_state["run_id"] = run_id
    _harness_state["events_queue"] = Queue()
    _harness_state["events_list"] = []  # Reset broadcast list
    _harness_state["events_counter"] = 0  # Reset counter
    _harness_state["start_time"] = datetime.now()

    # Start background thread
    thread = threading.Thread(
        target=_run_harness_thread,
        args=(config, run_id),
        daemon=True,
    )
    _harness_state["thread"] = thread
    thread.start()

    return HarnessRunResponse(run_id=run_id, status="started")


@router.get("/stream")
async def stream_harness_events():
    """Stream harness events via SSE."""

    async def event_generator():
        # Track which events this client has seen
        last_seen_id = -1

        # Send initial status
        yield f"data: {json.dumps({'type': 'connected', 'is_running': _harness_state['is_running']})}\n\n"

        while True:
            # Check for new events in broadcast list
            events_list = _harness_state["events_list"]
            for event in events_list:
                if event.get("_id", -1) > last_seen_id:
                    last_seen_id = event["_id"]
                    # Send event without internal _id
                    event_copy = {k: v for k, v in event.items() if k != "_id"}
                    yield f"data: {json.dumps(event_copy)}\n\n"

                    if event.get("type") == "done":
                        return

            # Small delay to prevent busy loop
            await asyncio.sleep(0.1)

            # Send heartbeat if not running
            if not _harness_state["is_running"] and last_seen_id == _harness_state["events_counter"] - 1:
                yield f"data: {json.dumps({'type': 'heartbeat', 'is_running': False})}\n\n"
                await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/status", response_model=HarnessStatusResponse)
async def get_harness_status():
    """Get current harness status."""
    elapsed = None
    if _harness_state.get("start_time") and _harness_state["is_running"]:
        elapsed = (datetime.now() - _harness_state["start_time"]).total_seconds()

    return HarnessStatusResponse(
        is_running=_harness_state["is_running"],
        run_id=_harness_state.get("run_id"),
        current_experiment=_harness_state.get("current_experiment"),
        progress=None,  # TODO: track progress
        elapsed_seconds=elapsed,
    )


@router.post("/stop")
async def stop_harness():
    """Stop the running harness."""
    global _harness_state

    if not _harness_state["is_running"]:
        raise HTTPException(status_code=400, detail="Harness is not running")

    # Signal stop (the thread will check this)
    _harness_state["is_running"] = False
    _emit_event({"type": "stopped", "timestamp": datetime.now().isoformat()})

    return {"status": "stopping"}


@router.get("/experiments")
async def list_experiments():
    """List all experiments from tracker."""
    tracker = ExperimentTracker(storage_dir="./experiments")
    experiments = tracker.get_all()

    return {
        "experiments": [
            {
                "id": e.id,
                "ticker": e.idea.ticker,
                "name": e.idea.name,
                "narrative": e.idea.narrative[:100] + "..." if len(e.idea.narrative) > 100 else e.idea.narrative,
                "hook": e.idea.hook,
                "strategy": e.idea.strategy.value,
                "meme_style": e.idea.meme_style.value,
                "status": e.status.value,
                "score": e.score,
                "outcome": e.result.predicted_outcome if e.result else None,
                "viral_coefficient": e.result.viral_coefficient if e.result else None,
                "peak_sentiment": e.result.peak_sentiment if e.result else None,
                "fud_resistance": e.result.fud_resistance if e.result else None,
                "total_engagement": e.result.total_engagement if e.result else None,
                "dominant_narrative": e.result.dominant_narrative if e.result else None,
                "created_at": e.created_at,
            }
            for e in sorted(experiments, key=lambda x: x.created_at, reverse=True)[:50]
        ]
    }


@router.get("/leaderboard")
async def get_leaderboard():
    """Get top performing experiments."""
    tracker = ExperimentTracker(storage_dir="./experiments")
    top = tracker.get_top_performers(10)

    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "id": e.id,
                "ticker": e.idea.ticker,
                "name": e.idea.name,
                "score": e.score,
                "outcome": e.result.predicted_outcome if e.result else None,
                "strategy": e.idea.strategy.value,
                "viral_coefficient": e.result.viral_coefficient if e.result else None,
            }
            for i, e in enumerate(top)
        ]
    }


@router.get("/learnings")
async def get_learnings():
    """Get accumulated learnings from experiments."""
    tracker = ExperimentTracker(storage_dir="./experiments")
    summary = tracker.get_summary()
    learnings = tracker.get_learnings()

    return {
        "summary": {
            "total_experiments": summary.total_experiments,
            "completed": summary.completed,
            "failed": summary.failed,
            "avg_score": summary.avg_score,
            "top_score": summary.top_score,
        },
        "strategy_performance": summary.strategy_performance,
        "style_performance": summary.style_performance,
        "outcome_distribution": summary.outcome_distribution,
        "insights": learnings.get("insights", []),
    }
