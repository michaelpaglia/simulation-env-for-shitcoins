"""
Example: Autonomous Testing Harness

This demonstrates how to use the harness to run autonomous experiments
with AI-generated token ideas.

Usage:
    python examples/autonomous_harness.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.harness import (
    AutonomousRunner,
    RunConfig,
    RunMode,
    IdeaGenerator,
    IdeaStrategy,
    ExperimentTracker,
)
from src.models.token import MarketCondition


def example_basic_run():
    """Run a basic autonomous experiment session."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Autonomous Run")
    print("="*60)

    runner = AutonomousRunner()

    config = RunConfig(
        mode=RunMode.BALANCED,
        max_experiments=3,
        simulation_hours=24,
        market_condition=MarketCondition.CRAB,
        verbose=True,
    )

    result = runner.run(config)

    print(f"\nBest performer: {result.best_experiment.idea.name if result.best_experiment else 'None'}")
    return result


def example_targeted_run():
    """Run experiments targeting a specific theme."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Targeted Theme Run")
    print("="*60)

    runner = AutonomousRunner()

    config = RunConfig(
        mode=RunMode.TARGETED,
        max_experiments=3,
        simulation_hours=24,
        target_theme="cats and internet culture",
        verbose=True,
    )

    result = runner.run(config)
    return result


def example_brainstorm():
    """Brainstorm ideas around a theme and test them."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Brainstorm and Test")
    print("="*60)

    runner = AutonomousRunner()

    experiments = runner.brainstorm_and_test(
        theme="AI agents gone rogue",
        num_ideas=3,
        simulation_hours=24,
        verbose=True,
    )

    return experiments


def example_exploit_mode():
    """Run in exploit mode - focus on what's working."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Exploit Mode (after learning)")
    print("="*60)

    runner = AutonomousRunner()

    # First, do some exploration
    explore_config = RunConfig(
        mode=RunMode.EXPLORE,
        max_experiments=5,
        simulation_hours=12,
        verbose=True,
    )
    runner.run(explore_config)

    # Then, exploit what worked
    exploit_config = RunConfig(
        mode=RunMode.EXPLOIT,
        max_experiments=3,
        simulation_hours=24,
        verbose=True,
    )
    result = runner.run(exploit_config)

    return result


def example_view_learnings():
    """View learnings from past experiments."""
    print("\n" + "="*60)
    print("EXAMPLE 5: View Accumulated Learnings")
    print("="*60)

    tracker = ExperimentTracker()

    # Summary
    summary = tracker.get_summary()
    print(f"\nTotal experiments: {summary.total_experiments}")
    print(f"Completed: {summary.completed}")
    print(f"Average score: {summary.avg_score:.2%}")

    # Learnings
    learnings = tracker.get_learnings()
    print("\nInsights:")
    for insight in learnings.get("insights", []):
        print(f"  - {insight}")

    # Top performers
    print("\nTop performers:")
    for exp in tracker.get_top_performers(5):
        print(f"  - {exp.idea.name}: {exp.score:.2%}")


def example_idea_generator():
    """Use the idea generator directly."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Direct Idea Generation")
    print("="*60)

    generator = IdeaGenerator()

    # Generate ideas with different strategies
    for strategy in [IdeaStrategy.CONTRARIAN, IdeaStrategy.NOSTALGIA, IdeaStrategy.REMIX]:
        print(f"\n--- {strategy.value.upper()} ---")
        ideas = generator.generate(
            strategy=strategy,
            market_condition=MarketCondition.BULL,
            num_ideas=1,
        )
        if ideas:
            idea = ideas[0]
            print(f"Name: {idea.name} (${idea.ticker})")
            print(f"Hook: {idea.hook}")
            print(f"Confidence: {idea.confidence:.0%}")


def example_custom_callbacks():
    """Use custom callbacks for monitoring."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Custom Callbacks")
    print("="*60)

    def on_start(exp):
        print(f"  [START] Testing: {exp.idea.name}")

    def on_complete(exp):
        emoji = "✓" if exp.score and exp.score > 0.5 else "✗"
        print(f"  [{emoji}] {exp.idea.name}: {exp.score:.2%}" if exp.score else f"  [✗] {exp.idea.name}: FAILED")

    def on_run_complete(experiments):
        completed = [e for e in experiments if e.score]
        print(f"\n  Run complete! {len(completed)}/{len(experiments)} successful")

    runner = AutonomousRunner()

    config = RunConfig(
        max_experiments=3,
        simulation_hours=12,
        on_experiment_start=on_start,
        on_experiment_complete=on_complete,
        on_run_complete=on_run_complete,
        verbose=False,  # We're using our own output
    )

    runner.run(config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous Harness Examples")
    parser.add_argument("example", nargs="?", choices=[
        "basic", "targeted", "brainstorm", "exploit", "learnings", "generator", "callbacks", "all"
    ], default="basic", help="Which example to run")

    args = parser.parse_args()

    examples = {
        "basic": example_basic_run,
        "targeted": example_targeted_run,
        "brainstorm": example_brainstorm,
        "exploit": example_exploit_mode,
        "learnings": example_view_learnings,
        "generator": example_idea_generator,
        "callbacks": example_custom_callbacks,
    }

    if args.example == "all":
        for name, func in examples.items():
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}")
    else:
        examples[args.example]()
