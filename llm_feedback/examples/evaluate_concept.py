"""
Evaluate a Shitcoin Concept

Test whether a token idea would work on CT before deploying.

Run with: python -m llm_feedback.examples.evaluate_concept
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from llm_feedback.token_evaluator import TokenEvaluator, TokenConcept


def main():
    print("=" * 60)
    print("SHITCOIN CONCEPT EVALUATOR")
    print("Test your token idea before deploying")
    print("=" * 60)

    # Define a concept to test
    concept = TokenConcept(
        name="GigaBrain",
        ticker="GIGA",
        narrative="AI agent that trades memecoins and posts its reasoning on Twitter",
        meme_style="ironic",
        target_audience="degens",
        hook="Watch an AI lose money in real-time",
        current_ct_mood="AI meta is hot, but oversaturated",
    )

    print(f"\nTesting concept:")
    print(concept.to_prompt())
    print("-" * 60)

    # Create evaluator (no simulation engine for quick eval)
    evaluator = TokenEvaluator(
        simulation_engine=None,  # Quick eval doesn't need simulation
        model="claude-sonnet-4-20250514",
    )

    # Quick evaluation (no full simulation)
    print("\nRunning quick concept evaluation...\n")

    try:
        feedback = evaluator.quick_evaluate(concept)

        print(f"VIABILITY SCORE: {feedback.viability_score:.0%}")
        print(f"PREDICTED OUTCOME: {feedback.predicted_outcome}")
        print(f"CONFIDENCE: {feedback.confidence:.0%}")

        print("\nSTRENGTHS:")
        for s in feedback.strengths:
            print(f"  + {s}")

        print("\nWEAKNESSES:")
        for w in feedback.weaknesses:
            print(f"  - {w}")

        print("\nSUGGESTIONS:")
        for s in feedback.suggestions:
            print(f"  > {s}")

        print(f"\nREASONING:\n{feedback.reasoning}")

        # Generate variations if viability is low
        if feedback.viability_score < 0.6:
            print("\n" + "=" * 60)
            print("Viability low. Generating improved variations...")
            print("=" * 60)

            variations = evaluator.iterate(concept, feedback)
            for i, var in enumerate(variations, 1):
                print(f"\nVariation {i}:")
                print(var.to_prompt())

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure ANTHROPIC_API_KEY is set in .env")


if __name__ == "__main__":
    main()
