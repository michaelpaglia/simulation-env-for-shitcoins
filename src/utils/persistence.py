"""Persistence utilities for saving and loading simulation results."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.token import SimulationResult


DEFAULT_SIMULATIONS_DIR = Path("simulations")


def _ensure_dir(directory: Path) -> None:
    """Create directory if it doesn't exist."""
    directory.mkdir(parents=True, exist_ok=True)


def _generate_filename(ticker: str, format: str = "json") -> str:
    """Generate a unique filename based on ticker and timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"{ticker}_{timestamp}.{format}"


def save_simulation(
    result: SimulationResult,
    path: Optional[Path] = None,
    format: str = "json",
    directory: Path = DEFAULT_SIMULATIONS_DIR,
) -> Path:
    """Save a simulation result to disk.

    Args:
        result: The SimulationResult to save
        path: Optional specific file path. If None, auto-generates filename.
        format: Output format - "json" (full fidelity) or "csv" (flattened metrics)
        directory: Directory to save to (default: ./simulations/)

    Returns:
        Path to the saved file

    Raises:
        ValueError: If format is not supported
    """
    if format not in ("json", "csv"):
        raise ValueError(f"Unsupported format '{format}'. Use 'json' or 'csv'.")

    _ensure_dir(directory)

    if path is None:
        filename = _generate_filename(result.token.ticker, format)
        path = directory / filename

    if format == "json":
        _save_json(result, path)
    else:
        _save_csv(result, path)

    return path


def _save_json(result: SimulationResult, path: Path) -> None:
    """Save result as JSON with full fidelity."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))


def _save_csv(result: SimulationResult, path: Path) -> None:
    """Save result as flattened CSV for spreadsheet analysis."""
    # Flatten nested token into prefixed columns
    flat_data = {
        "token_name": result.token.name,
        "token_ticker": result.token.ticker,
        "token_narrative": result.token.narrative,
        "token_meme_style": result.token.meme_style.value,
        "token_tagline": result.token.tagline or "",
        "token_market_condition": result.token.market_condition.value,
        "viral_coefficient": result.viral_coefficient,
        "peak_sentiment": result.peak_sentiment,
        "sentiment_stability": result.sentiment_stability,
        "fud_resistance": result.fud_resistance,
        "total_mentions": result.total_mentions,
        "total_engagement": result.total_engagement,
        "influencer_pickups": result.influencer_pickups,
        "hours_to_peak": result.hours_to_peak,
        "hours_to_death": result.hours_to_death or "",
        "dominant_narrative": result.dominant_narrative,
        "top_fud_points": "; ".join(result.top_fud_points),
        "predicted_outcome": result.predicted_outcome,
        "confidence": result.confidence,
    }

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        writer.writeheader()
        writer.writerow(flat_data)


def load_simulation(path: Path) -> SimulationResult:
    """Load a simulation result from disk.

    Args:
        path: Path to the JSON file

    Returns:
        SimulationResult object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid JSON simulation
    """
    if not path.exists():
        raise FileNotFoundError(f"Simulation file not found: {path}")

    if path.suffix != ".json":
        raise ValueError("Only JSON files can be loaded. CSV is export-only.")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return SimulationResult.model_validate(data)


def list_simulations(directory: Path = DEFAULT_SIMULATIONS_DIR) -> list[dict]:
    """List all saved simulations with metadata.

    Args:
        directory: Directory to scan (default: ./simulations/)

    Returns:
        List of dicts with filename, ticker, timestamp, and path
    """
    if not directory.exists():
        return []

    simulations = []

    for file in sorted(directory.glob("*.json"), reverse=True):
        # Parse filename: TICKER_YYYY-MM-DD_HHMMSS.json
        parts = file.stem.rsplit("_", 2)
        if len(parts) >= 3:
            ticker = parts[0]
            date_str = parts[1]
            time_str = parts[2]
            try:
                timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y-%m-%d_%H%M%S")
            except ValueError:
                timestamp = None
        else:
            ticker = file.stem
            timestamp = None

        simulations.append({
            "filename": file.name,
            "ticker": ticker,
            "timestamp": timestamp,
            "path": file,
        })

    return simulations


def get_latest_simulation(
    ticker: Optional[str] = None,
    directory: Path = DEFAULT_SIMULATIONS_DIR,
) -> Optional[Path]:
    """Get the most recent simulation file, optionally filtered by ticker.

    Args:
        ticker: Optional ticker to filter by
        directory: Directory to scan

    Returns:
        Path to most recent simulation, or None if none found
    """
    simulations = list_simulations(directory)

    if ticker:
        ticker_upper = ticker.upper()
        simulations = [s for s in simulations if s["ticker"].upper() == ticker_upper]

    if not simulations:
        return None

    # Already sorted by most recent first
    return simulations[0]["path"]
