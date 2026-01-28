"""
Run CT Simulation with LLM Feedback

Full integration test - runs the actual CT simulation engine
with LLM observation and concept evaluation.

Run with: python -m llm_feedback.examples.run_ct_evaluation
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from llm_feedback.ct_integration import CTConceptEvaluator
from llm_feedback.token_evaluator import TokenConcept


def main():
    print("=" * 60)
    print("CT SIMULATION + LLM FEEDBACK")
    print("Testing token concept with synthetic CT simulation")
    print("=" * 60)

    # Define concept to test
    concept = TokenConcept(
        name="GigaBrain",
        ticker="GIGA",
        narrative="AI agent that trades memecoins and posts its reasoning on Twitter",
        meme_style="ironic",
        target_audience="degens",
        hook="Watch an AI lose money in real-time",
        current_ct_mood="AI meta is hot but crowded",
    )

    print(f"\nTesting: {concept.name} (${concept.ticker})")
    print(f"Narrative: {concept.narrative}")
    print(f"Hook: {concept.hook}")

    # Create evaluator
    evaluator = CTConceptEvaluator()

    # Run full simulation with LLM checkpoints
    sim_result, feedback = evaluator.evaluate(
        concept=concept,
        hours=18,         # 18-hour simulation
        analyze_every=9,  # LLM analyzes every 9 hours (2 checkpoints)
        verbose=True,
    )

    # Print detailed feedback
    print("\n" + "=" * 60)
    print("CONCEPT EVALUATION")
    print("=" * 60)

    print(f"\nVIABILITY SCORE: {feedback.viability_score:.0%}")
    print(f"PREDICTED OUTCOME: {feedback.predicted_outcome}")
    print(f"CONFIDENCE: {feedback.confidence:.0%}")

    print("\nSTRENGTHS:")
    for s in feedback.strengths[:5]:
        print(f"  + {s}")

    print("\nWEAKNESSES:")
    for w in feedback.weaknesses[:5]:
        print(f"  - {w}")

    print("\nSUGGESTIONS:")
    for s in feedback.suggestions[:5]:
        print(f"  > {s}")

    print(f"\nREASONING: {feedback.reasoning}")


if __name__ == "__main__":
    main()
