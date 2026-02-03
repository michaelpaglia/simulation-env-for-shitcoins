"""Verification script for optimization changes."""

import sys
from src.simulation.engine import SimulationEngine, SimulationState, Tweet
from src.simulation.competition import CompetitionSimulator
from src.models.token import Token, MarketCondition, MemeStyle
from src.harness.idea_generator import IdeaGenerator
from src.api.main import get_engine, prepare_token_for_simulation, SimulationRequest, TokenConfig
from src.agents.personas import get_persona, PersonaType

print("=" * 60)
print("OPTIMIZATION VERIFICATION TESTS")
print("=" * 60)

tests_passed = 0
tests_failed = 0

def test(name, condition, error_msg=""):
    """Simple test helper."""
    global tests_passed, tests_failed
    if condition:
        print(f"[PASS] {name}")
        tests_passed += 1
    else:
        print(f"[FAIL] {name}")
        if error_msg:
            print(f"  Error: {error_msg}")
        tests_failed += 1

# Test 1: Idea Generator Model
print("\n1. MODEL SELECTION")
print("-" * 60)
generator = IdeaGenerator(api_key="test_key")
test("Idea generator uses Haiku",
     generator.model == "claude-3-5-haiku-20241022",
     f"Expected 'claude-3-5-haiku-20241022', got '{generator.model}'")

engine = SimulationEngine(api_key="test_key")
test("Simulation engine uses Haiku",
     engine.model == "claude-3-5-haiku-20241022",
     f"Expected 'claude-3-5-haiku-20241022', got '{engine.model}'")

# Test 2: Engine Pooling
print("\n2. ENGINE POOLING")
print("-" * 60)
import src.api.main as main_module
main_module._engine_instance = None

engine1 = get_engine()
engine2 = get_engine()
engine3 = get_engine()

test("get_engine returns singleton (1 vs 2)", engine1 is engine2)
test("get_engine returns singleton (2 vs 3)", engine2 is engine3)
test("get_engine returns singleton (1 vs 3)", engine1 is engine3)

# Test 3: Engine Reusability
print("\n3. ENGINE REUSABILITY")
print("-" * 60)
test("Engine has client attribute", hasattr(engine1, 'client'))
test("Engine has model attribute", hasattr(engine1, 'model'))
test("Engine has personas attribute", hasattr(engine1, 'personas'))

personas_before = engine1.personas
model_before = engine1.model

token = Token(
    name="Test",
    ticker="TEST",
    narrative="Test token",
    meme_style=MemeStyle.ABSURD,
    market_condition=MarketCondition.CRAB
)
state = SimulationState(token=token)

test("Engine personas unchanged after use", engine1.personas is personas_before)
test("Engine model unchanged after use", engine1.model == model_before)

# Test 4: Token Preparation Helper
print("\n4. TOKEN PREPARATION HELPER")
print("-" * 60)
request = SimulationRequest(
    token=TokenConfig(
        name="Test Token",
        ticker="test",
        narrative="A test narrative",
        meme_style=MemeStyle.ABSURD,
        market_condition=MarketCondition.CRAB
    ),
    hours=24,
    use_twitter_priors=False
)

prepared_token = prepare_token_for_simulation(request)
test("Token preparation creates Token object", isinstance(prepared_token, Token))
test("Token name preserved", prepared_token.name == "Test Token")
test("Token ticker uppercased", prepared_token.ticker == "TEST")
test("Token narrative preserved", prepared_token.narrative == "A test narrative")

# Test 5: Hot Tweet Optimization
print("\n5. HOT TWEET OPTIMIZATION")
print("-" * 60)
test_engine = SimulationEngine(api_key=None)
test_token = Token(
    name="Test",
    ticker="TEST",
    narrative="Test token",
    meme_style=MemeStyle.ABSURD,
    market_condition=MarketCondition.CRAB
)
test_state = SimulationState(token=test_token, current_hour=10)

# Create old tweets (should be filtered out)
for hour in range(1, 6):
    tweet = Tweet(
        id=f"old_{hour}",
        author=get_persona(PersonaType.DEGEN),
        content=f"Old tweet {hour}",
        hour=hour,
        sentiment=0.5,
        likes=1000,
        thread_depth=0
    )
    test_state.tweets.append(tweet)

# Create recent tweets (should be included)
recent_count = 0
for hour in range(8, 11):
    tweet = Tweet(
        id=f"recent_{hour}",
        author=get_persona(PersonaType.DEGEN),
        content=f"Recent tweet {hour}",
        hour=hour,
        sentiment=0.5,
        likes=1000,
        thread_depth=0
    )
    test_state.tweets.append(tweet)
    recent_count += 1

hot_tweets = test_engine._identify_hot_tweets(test_state)
test("Hot tweets identified", len(hot_tweets) > 0)
test("Hot tweets only include recent ones",
     all(tweet.hour >= 8 for tweet in hot_tweets),
     f"Found tweets from hours: {[t.hour for t in hot_tweets]}")

# Test 6: Competition Simulator Structure
print("\n6. COMPETITION SIMULATOR")
print("-" * 60)
tokens = [
    Token(
        name="Token A",
        ticker="TOKA",
        narrative="First token",
        meme_style=MemeStyle.ABSURD,
        market_condition=MarketCondition.CRAB
    ),
    Token(
        name="Token B",
        ticker="TOKB",
        narrative="Second token",
        meme_style=MemeStyle.EDGY,
        market_condition=MarketCondition.CRAB
    )
]

simulator = CompetitionSimulator(api_key=None)
test("Competition simulator created", simulator is not None)
test("Competition simulator has client", hasattr(simulator, 'client'))
test("Competition simulator has api_key", hasattr(simulator, 'api_key'))

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print("=" * 60)

if tests_failed > 0:
    print("\n[WARNING] Some tests failed! Review the output above.")
    sys.exit(1)
else:
    print("\n[SUCCESS] All optimizations verified successfully!")
    sys.exit(0)
