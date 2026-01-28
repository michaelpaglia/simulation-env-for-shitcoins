"""CLI for running shitcoin simulations."""

import os
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .models.token import Token, MarketCondition, MemeStyle
from .simulation.engine import SimulationEngine
from .presets import get_preset, list_presets, get_preset_info
from .harness import (
    AutonomousRunner,
    RunConfig,
    RunMode,
    IdeaGenerator,
    IdeaStrategy,
    ExperimentTracker,
    ExperimentStatus,
)

load_dotenv()

app = typer.Typer(help="Shitcoin Social Simulation Environment")
console = Console()

# Subcommand group for harness
harness_app = typer.Typer(help="Autonomous testing harness commands")
app.add_typer(harness_app, name="harness")


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

    api_key = os.getenv("ANTHROPIC_API_KEY") or None

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

    api_key = os.getenv("ANTHROPIC_API_KEY") or None
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

    api_key = os.getenv("ANTHROPIC_API_KEY") or None
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


# ============================================================================
# HARNESS COMMANDS - Autonomous testing
# ============================================================================


@harness_app.command("run")
def harness_run(
    experiments: int = typer.Option(10, "--experiments", "-n", help="Number of experiments to run"),
    mode: str = typer.Option("balanced", "--mode", "-m", help="Run mode: explore, exploit, balanced, targeted"),
    hours: int = typer.Option(24, "--hours", "-h", help="Simulation hours per experiment"),
    market: MarketCondition = typer.Option(MarketCondition.CRAB, "--market", help="Market condition"),
    theme: str = typer.Option(None, "--theme", help="Theme for targeted mode"),
    strategy: str = typer.Option(None, "--strategy", "-s", help="Strategy for targeted mode"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
):
    """Run autonomous experiments with AI-generated ideas."""

    api_key = os.getenv("ANTHROPIC_API_KEY") or None or None  # Convert empty string to None

    if not api_key:
        console.print("[yellow]Warning: No ANTHROPIC_API_KEY found. Using template mode.[/yellow]")
        console.print("Set ANTHROPIC_API_KEY for AI-powered idea generation.\n")

    # Map mode string to enum
    mode_map = {
        "explore": RunMode.EXPLORE,
        "exploit": RunMode.EXPLOIT,
        "balanced": RunMode.BALANCED,
        "targeted": RunMode.TARGETED,
    }
    run_mode = mode_map.get(mode.lower(), RunMode.BALANCED)

    # Map strategy string to enum if provided
    target_strategy = None
    if strategy:
        strategy_map = {
            "trend": IdeaStrategy.TREND_CHASE,
            "trend_chase": IdeaStrategy.TREND_CHASE,
            "contrarian": IdeaStrategy.CONTRARIAN,
            "remix": IdeaStrategy.REMIX,
            "avant_garde": IdeaStrategy.AVANT_GARDE,
            "nostalgia": IdeaStrategy.NOSTALGIA,
            "topical": IdeaStrategy.TOPICAL,
        }
        target_strategy = strategy_map.get(strategy.lower())

    config = RunConfig(
        mode=run_mode,
        max_experiments=experiments,
        simulation_hours=hours,
        market_condition=market,
        target_strategy=target_strategy,
        target_theme=theme,
        verbose=not quiet,
    )

    runner = AutonomousRunner(api_key=api_key)

    console.print(Panel(
        f"Mode: {run_mode.value}\n"
        f"Experiments: {experiments}\n"
        f"Hours per sim: {hours}\n"
        f"Market: {market.value}",
        title="Autonomous Run",
        border_style="blue"
    ))

    result = runner.run(config)

    # Final summary
    if result.best_experiment:
        console.print(Panel(
            f"Name: {result.best_experiment.idea.name}\n"
            f"Ticker: ${result.best_experiment.idea.ticker}\n"
            f"Score: {result.best_experiment.score:.2%}\n"
            f"Hook: {result.best_experiment.idea.hook}",
            title="Best Performer",
            border_style="green"
        ))


@harness_app.command("brainstorm")
def harness_brainstorm(
    theme: str = typer.Argument(..., help="Theme to brainstorm around"),
    ideas: int = typer.Option(5, "--ideas", "-n", help="Number of ideas to generate"),
    test: bool = typer.Option(True, "--test/--no-test", help="Run simulations on ideas"),
    hours: int = typer.Option(24, "--hours", "-h", help="Simulation hours if testing"),
):
    """Brainstorm ideas around a theme and optionally test them."""

    api_key = os.getenv("ANTHROPIC_API_KEY") or None or None

    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY required for brainstorming.[/red]")
        raise typer.Exit(code=1)

    runner = AutonomousRunner(api_key=api_key)

    console.print(f"\n[bold]Brainstorming around:[/bold] {theme}\n")

    if test:
        experiments = runner.brainstorm_and_test(
            theme=theme,
            num_ideas=ideas,
            simulation_hours=hours,
            verbose=True,
        )
    else:
        generator = IdeaGenerator(api_key=api_key)
        generated = generator.brainstorm(theme, ideas)

        table = Table(title=f"Ideas for '{theme}'")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Ticker", style="yellow")
        table.add_column("Hook", style="green")
        table.add_column("Confidence", style="magenta")

        for i, idea in enumerate(generated, 1):
            table.add_row(
                str(i),
                idea.name,
                f"${idea.ticker}",
                idea.hook[:50] + "..." if len(idea.hook) > 50 else idea.hook,
                f"{idea.confidence:.0%}",
            )

        console.print(table)


@harness_app.command("generate")
def harness_generate(
    count: int = typer.Option(3, "--count", "-n", help="Number of ideas to generate"),
    strategy: str = typer.Option(None, "--strategy", "-s", help="Generation strategy"),
    market: MarketCondition = typer.Option(MarketCondition.CRAB, "--market", help="Market condition"),
):
    """Generate token ideas without running simulations."""

    api_key = os.getenv("ANTHROPIC_API_KEY") or None or None

    if not api_key:
        console.print("[yellow]No API key - using template ideas[/yellow]\n")

    generator = IdeaGenerator(api_key=api_key)

    # Map strategy
    target_strategy = None
    if strategy:
        strategy_map = {
            "trend": IdeaStrategy.TREND_CHASE,
            "contrarian": IdeaStrategy.CONTRARIAN,
            "remix": IdeaStrategy.REMIX,
            "avant_garde": IdeaStrategy.AVANT_GARDE,
            "nostalgia": IdeaStrategy.NOSTALGIA,
            "topical": IdeaStrategy.TOPICAL,
        }
        target_strategy = strategy_map.get(strategy.lower())

    with console.status("[bold green]Generating ideas..."):
        ideas = generator.generate(
            strategy=target_strategy,
            market_condition=market,
            num_ideas=count,
        )

    for i, idea in enumerate(ideas, 1):
        console.print(Panel(
            f"[bold cyan]{idea.name}[/bold cyan] (${idea.ticker})\n\n"
            f"[bold]Narrative:[/bold] {idea.narrative}\n\n"
            f"[bold]Hook:[/bold] {idea.hook}\n\n"
            f"[bold]Tagline:[/bold] {idea.tagline}\n\n"
            f"[dim]Strategy: {idea.strategy.value} | Style: {idea.meme_style.value} | Confidence: {idea.confidence:.0%}[/dim]\n\n"
            f"[yellow]Risks:[/yellow] {', '.join(idea.risk_factors)}",
            title=f"Idea #{i}",
            border_style="blue"
        ))


@harness_app.command("status")
def harness_status():
    """Show experiment tracker status and top performers."""

    tracker = ExperimentTracker()
    summary = tracker.get_summary()

    # Overall status
    console.print(Panel(
        f"Total: {summary.total_experiments}\n"
        f"Completed: {summary.completed}\n"
        f"Failed: {summary.failed}\n"
        f"Pending: {summary.pending}\n\n"
        f"Avg Score: {summary.avg_score:.2%}\n"
        f"Top Score: {summary.top_score:.2%}",
        title="Experiment Status",
        border_style="blue"
    ))

    # Top performers
    top = tracker.get_top_performers(5)
    if top:
        table = Table(title="Top Performers")
        table.add_column("Rank", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Ticker", style="yellow")
        table.add_column("Score", style="green")
        table.add_column("Outcome", style="magenta")

        for i, exp in enumerate(top, 1):
            table.add_row(
                str(i),
                exp.idea.name,
                f"${exp.idea.ticker}",
                f"{exp.score:.2%}" if exp.score else "N/A",
                exp.result.predicted_outcome if exp.result else "N/A",
            )

        console.print(table)

    # Strategy performance
    if summary.strategy_performance:
        table = Table(title="Strategy Performance")
        table.add_column("Strategy", style="cyan")
        table.add_column("Avg Score", style="green")

        for strat, score in sorted(summary.strategy_performance.items(), key=lambda x: x[1], reverse=True):
            table.add_row(strat, f"{score:.2%}")

        console.print(table)


@harness_app.command("report")
def harness_report(
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate a full experiment report."""

    tracker = ExperimentTracker()
    report = tracker.export_report(output)

    if output:
        console.print(f"[green]Report saved to: {output}[/green]")
    else:
        console.print(report)


@harness_app.command("learnings")
def harness_learnings():
    """Show learnings extracted from experiments."""

    tracker = ExperimentTracker()
    learnings = tracker.get_learnings()

    console.print(Panel(
        f"Experiments analyzed: {learnings.get('total_analyzed', 0)}\n"
        f"Success rate: {learnings.get('success_rate', 0):.1%}",
        title="Learnings",
        border_style="blue"
    ))

    insights = learnings.get("insights", [])
    if insights:
        console.print("\n[bold]Key Insights:[/bold]")
        for insight in insights:
            console.print(f"  • {insight}")

    winning = learnings.get("winning_patterns", {})
    if winning.get("strategies"):
        console.print("\n[bold green]Winning Strategies:[/bold green]")
        for strat, count in winning["strategies"].items():
            console.print(f"  {strat}: {count} wins")

    losing = learnings.get("losing_patterns", {})
    if losing.get("strategies"):
        console.print("\n[bold red]Losing Strategies:[/bold red]")
        for strat, count in losing["strategies"].items():
            console.print(f"  {strat}: {count} losses")


if __name__ == "__main__":
    app()
