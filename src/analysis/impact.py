"""Persona impact analysis for simulation results."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if TYPE_CHECKING:
    from ..simulation.engine import Tweet

from ..agents.personas import PersonaType


@dataclass
class PersonaImpact:
    """Impact metrics for a single persona type."""

    persona_type: PersonaType
    tweet_count: int
    avg_sentiment: float
    total_engagement: int
    sentiment_contribution: float  # Engagement-weighted sentiment
    pct_of_total_engagement: float


@dataclass
class ImpactReport:
    """Full impact analysis report."""

    token_ticker: str
    simulation_hours: int
    total_tweets: int
    total_engagement: int
    persona_impacts: list[PersonaImpact] = field(default_factory=list)

    @property
    def top_contributor(self) -> str:
        """Persona type with highest engagement share."""
        if not self.persona_impacts:
            return "N/A"
        top = max(self.persona_impacts, key=lambda p: p.pct_of_total_engagement)
        return top.persona_type.value

    @property
    def hype_sources(self) -> list[str]:
        """Persona types that drove positive sentiment."""
        return [
            p.persona_type.value
            for p in self.persona_impacts
            if p.avg_sentiment > 0.2
        ]

    @property
    def fud_sources(self) -> list[str]:
        """Persona types that generated FUD."""
        return [
            p.persona_type.value
            for p in self.persona_impacts
            if p.avg_sentiment < -0.2
        ]


def analyze_impact(tweets: list["Tweet"], ticker: str = "TOKEN") -> ImpactReport:
    """Analyze persona impact from simulation tweets.

    Args:
        tweets: List of Tweet objects from simulation
        ticker: Token ticker for the report

    Returns:
        ImpactReport with per-persona breakdown
    """
    if not tweets:
        return ImpactReport(
            token_ticker=ticker,
            simulation_hours=0,
            total_tweets=0,
            total_engagement=0,
        )

    # Group tweets by persona type
    by_type: dict[PersonaType, list] = defaultdict(list)
    for tweet in tweets:
        by_type[tweet.author.type].append(tweet)

    # Calculate total engagement
    total_engagement = sum(
        t.likes + t.retweets + t.replies for t in tweets
    )

    # Calculate per-persona metrics
    persona_impacts = []

    for persona_type, type_tweets in by_type.items():
        tweet_count = len(type_tweets)

        # Average sentiment
        avg_sentiment = sum(t.sentiment for t in type_tweets) / tweet_count

        # Total engagement for this persona type
        type_engagement = sum(
            t.likes + t.retweets + t.replies for t in type_tweets
        )

        # Sentiment contribution (engagement-weighted)
        # This shows how much this persona type shifted overall sentiment
        sentiment_contribution = sum(
            t.sentiment * (t.likes + t.retweets + t.replies)
            for t in type_tweets
        )

        # Percentage of total engagement
        pct_engagement = (type_engagement / total_engagement * 100) if total_engagement > 0 else 0

        persona_impacts.append(PersonaImpact(
            persona_type=persona_type,
            tweet_count=tweet_count,
            avg_sentiment=avg_sentiment,
            total_engagement=type_engagement,
            sentiment_contribution=sentiment_contribution,
            pct_of_total_engagement=pct_engagement,
        ))

    # Sort by engagement percentage (highest first)
    persona_impacts.sort(key=lambda p: p.pct_of_total_engagement, reverse=True)

    # Get simulation hours from last tweet
    max_hour = max(t.hour for t in tweets)

    return ImpactReport(
        token_ticker=ticker,
        simulation_hours=max_hour,
        total_tweets=len(tweets),
        total_engagement=total_engagement,
        persona_impacts=persona_impacts,
    )


def format_impact_report(report: ImpactReport, console: Console = None) -> None:
    """Print a formatted impact report using Rich.

    Args:
        report: ImpactReport to display
        console: Rich console (creates one if not provided)
    """
    if console is None:
        console = Console()

    # Header
    console.print()
    console.print(Panel(
        f"[bold]Persona Impact Report: ${report.token_ticker}[/bold]\n"
        f"Duration: {report.simulation_hours} hours | "
        f"Tweets: {report.total_tweets} | "
        f"Engagement: {report.total_engagement:,}",
        border_style="cyan",
    ))

    # Main table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Persona", style="cyan")
    table.add_column("Tweets", justify="right")
    table.add_column("Avg Sent", justify="right")
    table.add_column("Engagement", justify="right", style="green")
    table.add_column("Impact %", justify="right", style="yellow")

    for impact in report.persona_impacts:
        # Color sentiment based on value
        if impact.avg_sentiment > 0.2:
            sent_style = "[green]"
        elif impact.avg_sentiment < -0.2:
            sent_style = "[red]"
        else:
            sent_style = "[dim]"

        table.add_row(
            impact.persona_type.value.upper(),
            str(impact.tweet_count),
            f"{sent_style}{impact.avg_sentiment:+.2f}[/]",
            f"{impact.total_engagement:,}",
            f"{impact.pct_of_total_engagement:.1f}%",
        )

    console.print(table)

    # Summary
    console.print()
    console.print(f"[bold]Top Contributor:[/bold] {report.top_contributor.upper()} "
                  f"({max(p.pct_of_total_engagement for p in report.persona_impacts):.1f}% of engagement)")

    if report.hype_sources:
        console.print(f"[bold green]Hype Drivers:[/bold green] {', '.join(s.upper() for s in report.hype_sources)}")

    if report.fud_sources:
        console.print(f"[bold red]FUD Sources:[/bold red] {', '.join(s.upper() for s in report.fud_sources)}")

    console.print()
