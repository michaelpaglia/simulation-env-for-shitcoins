"""CLI for running shitcoin simulations."""

import os
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

from .models.token import Token, MarketCondition, MemeStyle
from .simulation.engine import SimulationEngine
from .presets import get_preset, list_presets, get_preset_info

load_dotenv()

app = typer.Typer(help="Shitcoin Social Simulation Environment")
console = Console()


@app.command()
def simulate(
    name: str = typer.Option(..., "--name", "-n", help="Token name"),
    ticker: str = typer.Option(..., "--ticker", "-t", help="Token ticker"),
    narrative: str = typer.Option(..., "--narrative", help="Token narrative/story"),
    tagline: str = typer.Option(None, "--tagline", help="Catchy tagline"),
    meme_style: MemeStyle = typer.Option(MemeStyle.ABSURD, "--style", help="Meme aesthetic"),
    market: MarketCondition = typer.Option(MarketCondition.CRAB, "--market", help="Market condition"),
    hours: int = typer.Option(48, "--hours", "-h", help="Simulation hours"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Run a simulation for a token."""

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        console.print("[yellow]Warning: No ANTHROPIC_API_KEY found. Using template mode.[/yellow]")
        console.print("Set ANTHROPIC_API_KEY for AI-powered responses.\n")

    token = Token(
        name=name,
        ticker=ticker.upper(),
        narrative=narrative,
        tagline=tagline,
        meme_style=meme_style,
        market_condition=market,
    )

    console.print(Panel(token.get_pitch(), title="Token Configuration", border_style="blue"))
    console.print(f"\nRunning {hours}-hour simulation...\n")

    engine = SimulationEngine(api_key=api_key)

    with console.status("[bold green]Simulating CT reactions..."):
        result = engine.run_simulation(token, hours=hours, verbose=verbose)

    # Display results
    console.print(Panel(result.summary(), title="Simulation Results", border_style="green"))

    # Show sample tweets
    if result.token:
        console.print("\n[bold]Sample Tweets:[/bold]\n")
        tweets = engine.run_simulation(token, hours=6, verbose=False).token
        # Just show the last result's tweets from state - we'll improve this
        console.print("[dim]Run with --verbose to see tweet timeline[/dim]")


@app.command()
def quick(
    ticker: str = typer.Argument(None, help="Token ticker (optional if using --preset)"),
    vibe: str = typer.Argument("random memecoin", help="Quick description"),
    preset: str = typer.Option(None, "--preset", "-p", help="Use a preset template"),
):
    """Quick simulation with minimal config."""

    if preset:
        try:
            token = get_preset(preset, ticker_override=ticker)
            console.print(f"[bold]Using preset:[/bold] {preset}")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(code=1)
    elif ticker:
        token = Token(
            name=ticker,
            ticker=ticker.upper(),
            narrative=vibe,
        )
    else:
        console.print("[red]Error: Provide a ticker or use --preset[/red]")
        raise typer.Exit(code=1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    engine = SimulationEngine(api_key=api_key)

    console.print(f"[bold]Quick sim for ${token.ticker}[/bold]: {token.narrative}\n")

    with console.status("[bold green]Running quick simulation..."):
        result = engine.run_simulation(token, hours=24)

    # Compact output
    table = Table(title=f"${token.ticker} Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Viral Score", f"{result.viral_coefficient:.2f}x")
    table.add_row("Peak Sentiment", f"{result.peak_sentiment:+.2f}")
    table.add_row("FUD Resistance", f"{result.fud_resistance:.0%}")
    table.add_row("Prediction", result.predicted_outcome.upper())
    table.add_row("Confidence", f"{result.confidence:.0%}")

    console.print(table)
    console.print(f"\n[dim]CT says: \"{result.dominant_narrative}\"[/dim]")


@app.command()
def compare(
    tickers: list[str] = typer.Argument(..., help="Tickers to compare (space-separated)"),
    narrative: str = typer.Option("memecoin", "--narrative", help="Shared narrative"),
):
    """Compare multiple token names/tickers."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    engine = SimulationEngine(api_key=api_key)

    results = []

    console.print(f"[bold]Comparing {len(tickers)} tokens...[/bold]\n")

    for ticker in tickers:
        token = Token(name=ticker, ticker=ticker.upper(), narrative=narrative)

        with console.status(f"Simulating ${ticker.upper()}..."):
            result = engine.run_simulation(token, hours=24)
            results.append(result)

    # Comparison table
    table = Table(title="Token Comparison")
    table.add_column("Ticker", style="cyan")
    table.add_column("Viral", style="green")
    table.add_column("Sentiment", style="yellow")
    table.add_column("FUD Resist", style="red")
    table.add_column("Prediction", style="magenta")

    for r in sorted(results, key=lambda x: x.viral_coefficient, reverse=True):
        table.add_row(
            f"${r.token.ticker}",
            f"{r.viral_coefficient:.2f}x",
            f"{r.peak_sentiment:+.2f}",
            f"{r.fud_resistance:.0%}",
            r.predicted_outcome,
        )

    console.print(table)

    winner = max(results, key=lambda x: x.viral_coefficient)
    console.print(f"\n[bold green]Winner: ${winner.token.ticker}[/bold green]")


@app.command()
def presets():
    """List available token presets."""

    table = Table(title="Available Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Ticker", style="yellow")
    table.add_column("Style", style="green")
    table.add_column("Description", style="dim")

    for name in list_presets():
        info = get_preset_info(name)
        token = info["token"]
        table.add_row(
            name,
            f"${token.ticker}",
            token.meme_style.value,
            info["description"],
        )

    console.print(table)
    console.print("\n[dim]Usage: python -m src.cli quick --preset <name>[/dim]")


if __name__ == "__main__":
    app()
