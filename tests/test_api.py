"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create test client for API."""
    return TestClient(app)


class TestAPIHealth:
    """Tests for API health and status endpoints."""

    def test_root_endpoint(self, client):
        """Root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestSimulateEndpoint:
    """Tests for /simulate endpoint."""

    def test_simulate_valid_request(self, client):
        """Valid simulation request returns results."""
        response = client.post("/simulate", json={
            "token": {
                "name": "TestToken",
                "ticker": "TEST",
                "narrative": "A test token",
                "meme_style": "absurd",
                "market_condition": "crab"
            },
            "hours": 12
        })
        assert response.status_code == 200
        data = response.json()
        assert "tweets" in data
        assert "viral_coefficient" in data
        assert "predicted_outcome" in data

    def test_simulate_minimal_request(self, client):
        """Minimal request with required fields works."""
        response = client.post("/simulate", json={
            "token": {
                "name": "Min",
                "ticker": "MIN",
                "narrative": "Minimal test"
            }
        })
        assert response.status_code == 200

    def test_simulate_missing_ticker(self, client):
        """Missing ticker returns error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "NoTicker",
                "narrative": "Missing ticker"
            }
        })
        assert response.status_code == 422  # Validation error

    def test_simulate_missing_narrative(self, client):
        """Missing narrative returns error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "NoNarrative",
                "ticker": "NONE"
            }
        })
        assert response.status_code == 422

    def test_simulate_invalid_meme_style(self, client):
        """Invalid meme style returns validation error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test",
                "meme_style": "invalid_style"
            }
        })
        # 422 Unprocessable Entity is the correct status for Pydantic validation errors
        assert response.status_code == 422

    def test_simulate_invalid_market_condition(self, client):
        """Invalid market condition returns validation error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test",
                "market_condition": "super_bull"
            }
        })
        # 422 Unprocessable Entity is the correct status for Pydantic validation errors
        assert response.status_code == 422

    def test_simulate_returns_tweets(self, client):
        """Simulation returns tweet list."""
        response = client.post("/simulate", json={
            "token": {
                "name": "TweetTest",
                "ticker": "TWEET",
                "narrative": "Testing tweets"
            },
            "hours": 24
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tweets"], list)
        if len(data["tweets"]) > 0:
            tweet = data["tweets"][0]
            assert "id" in tweet
            assert "author_name" in tweet
            assert "content" in tweet
            assert "sentiment" in tweet

    def test_simulate_hours_bounds(self, client):
        """Hours parameter respects bounds."""
        # Valid hours
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test"
            },
            "hours": 168  # Max
        })
        assert response.status_code == 200

        # Invalid hours (too high)
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test"
            },
            "hours": 200  # Over max
        })
        assert response.status_code == 422

    def test_simulate_all_meme_styles(self, client):
        """All meme styles work."""
        styles = ["cute", "edgy", "absurd", "topical", "nostalgic"]
        for style in styles:
            response = client.post("/simulate", json={
                "token": {
                    "name": "Test",
                    "ticker": "TEST",
                    "narrative": "Test",
                    "meme_style": style
                },
                "hours": 6
            })
            assert response.status_code == 200, f"Style {style} failed"

    def test_simulate_all_market_conditions(self, client):
        """All market conditions work."""
        conditions = ["bear", "crab", "bull", "euphoria"]
        for condition in conditions:
            response = client.post("/simulate", json={
                "token": {
                    "name": "Test",
                    "ticker": "TEST",
                    "narrative": "Test",
                    "market_condition": condition
                },
                "hours": 6
            })
            assert response.status_code == 200, f"Condition {condition} failed"


class TestPersonasEndpoint:
    """Tests for /personas endpoint."""

    def test_personas_returns_list(self, client):
        """Personas endpoint returns persona list."""
        response = client.get("/personas")
        assert response.status_code == 200
        data = response.json()
        assert "personas" in data
        assert isinstance(data["personas"], list)
        assert len(data["personas"]) > 0

    def test_persona_has_required_fields(self, client):
        """Each persona has required fields."""
        response = client.get("/personas")
        data = response.json()
        for persona in data["personas"]:
            assert "type" in persona
            assert "name" in persona
            assert "handle" in persona
            assert "influence_score" in persona


class TestMarketSentimentEndpoint:
    """Tests for /market-sentiment endpoint."""

    def test_market_sentiment_without_twitter(self, client):
        """Market sentiment returns default without Twitter API."""
        response = client.get("/market-sentiment")
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "condition" in data

    def test_market_sentiment_with_tokens(self, client):
        """Market sentiment accepts token parameter."""
        response = client.get("/market-sentiment?tokens=DOGE,SHIB")
        assert response.status_code == 200


class TestTwitterPriorEndpoint:
    """Tests for /twitter-prior endpoint."""

    def test_twitter_prior_without_api(self, client):
        """Twitter prior returns error without API configured."""
        response = client.get("/twitter-prior?token=TEST")
        # Should return 503 if Twitter not configured
        assert response.status_code in [200, 503]


class TestErrorHandling:
    """Tests for API error handling."""

    def test_invalid_json(self, client):
        """Invalid JSON returns error."""
        response = client.post(
            "/simulate",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_empty_body(self, client):
        """Empty body returns error."""
        response = client.post(
            "/simulate",
            json={}
        )
        assert response.status_code == 422

    def test_wrong_method(self, client):
        """Wrong HTTP method returns error."""
        response = client.get("/simulate")
        assert response.status_code == 405


class TestImproveTokenEndpoint:
    """Tests for /improve-token endpoint."""

    def test_improve_token_valid_request(self, client):
        """Valid improve token request returns variations."""
        response = client.post("/improve-token", json={
            "token": {
                "name": "TestToken",
                "ticker": "TEST",
                "narrative": "A test token",
                "meme_style": "absurd",
                "market_condition": "crab"
            },
            "feedback": {
                "viability_score": 0.4,
                "strengths": ["Good meme potential"],
                "weaknesses": ["Weak narrative", "No clear hook"],
                "suggestions": ["Add a viral hook", "Improve narrative"],
                "predicted_outcome": "pump_and_dump",
                "reasoning": "Generic concept needs improvement",
                "confidence": 0.6
            }
        })
        # May return 503 if no API key, 500 if API error (rate limit, credits, etc.)
        assert response.status_code in [200, 500, 503]
        if response.status_code == 200:
            data = response.json()
            assert "variations" in data
            assert isinstance(data["variations"], list)

    def test_improve_token_missing_token(self, client):
        """Missing token returns validation error."""
        response = client.post("/improve-token", json={
            "feedback": {
                "viability_score": 0.5,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "predicted_outcome": "unknown",
                "reasoning": "",
                "confidence": 0.5
            }
        })
        assert response.status_code == 422

    def test_improve_token_missing_feedback(self, client):
        """Missing feedback returns validation error."""
        response = client.post("/improve-token", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test"
            }
        })
        assert response.status_code == 422

    def test_improve_token_variation_structure(self, client):
        """Variation response has expected structure."""
        response = client.post("/improve-token", json={
            "token": {
                "name": "StructTest",
                "ticker": "STRUCT",
                "narrative": "Testing structure",
                "meme_style": "absurd",
                "market_condition": "crab"
            },
            "feedback": {
                "viability_score": 0.3,
                "strengths": [],
                "weaknesses": ["Everything"],
                "suggestions": ["Start over"],
                "predicted_outcome": "slow_bleed",
                "reasoning": "Needs work",
                "confidence": 0.7
            }
        })
        if response.status_code == 200:
            data = response.json()
            if len(data["variations"]) > 0:
                variation = data["variations"][0]
                assert "name" in variation
                assert "ticker" in variation
                assert "narrative" in variation
                assert "hook" in variation
                assert "changes" in variation


class TestCompetitionEndpoint:
    """Tests for /simulate/competition endpoint."""

    def test_competition_valid_request(self, client):
        """Valid competition request returns results."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {
                    "name": "Token A",
                    "ticker": "TOKA",
                    "narrative": "First test token",
                    "meme_style": "absurd",
                    "market_condition": "crab"
                },
                {
                    "name": "Token B",
                    "ticker": "TOKB",
                    "narrative": "Second test token",
                    "meme_style": "cute",
                    "market_condition": "crab"
                }
            ],
            "hours": 12,
            "market_condition": "crab"
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "winner" in data
        assert "analysis" in data
        assert len(data["results"]) == 2

    def test_competition_minimum_tokens(self, client):
        """Competition requires at least 2 tokens."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {
                    "name": "Only One",
                    "ticker": "ONE",
                    "narrative": "Single token"
                }
            ],
            "hours": 12
        })
        assert response.status_code == 422

    def test_competition_maximum_tokens(self, client):
        """Competition allows up to 4 tokens."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": f"Token {i}", "ticker": f"TOK{i}", "narrative": f"Token {i}"}
                for i in range(5)  # 5 tokens - over limit
            ],
            "hours": 12
        })
        assert response.status_code == 422

    def test_competition_four_tokens(self, client):
        """Competition works with 4 tokens."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": f"Token {i}", "ticker": f"TOK{i}", "narrative": f"Token {i}"}
                for i in range(4)
            ],
            "hours": 6
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 4

    def test_competition_result_structure(self, client):
        """Competition result has expected structure."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": "Alpha", "ticker": "ALPHA", "narrative": "First"},
                {"name": "Beta", "ticker": "BETA", "narrative": "Second"}
            ],
            "hours": 6
        })
        assert response.status_code == 200
        data = response.json()

        for result in data["results"]:
            assert "token" in result
            assert "viral_coefficient" in result
            assert "peak_sentiment" in result
            assert "total_engagement" in result
            assert "influencer_pickups" in result
            assert "predicted_outcome" in result
            assert "confidence" in result
            assert "rank" in result
            assert "market_share" in result

    def test_competition_ranks_ordered(self, client):
        """Competition results are ranked correctly."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": "A", "ticker": "A", "narrative": "Token A"},
                {"name": "B", "ticker": "B", "narrative": "Token B"},
                {"name": "C", "ticker": "C", "narrative": "Token C"}
            ],
            "hours": 6
        })
        assert response.status_code == 200
        data = response.json()

        ranks = [r["rank"] for r in data["results"]]
        assert sorted(ranks) == [1, 2, 3]

    def test_competition_winner_is_rank_one(self, client):
        """Winner ticker matches rank 1 result."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": "X", "ticker": "TOKX", "narrative": "Token X"},
                {"name": "Y", "ticker": "TOKY", "narrative": "Token Y"}
            ],
            "hours": 6
        })
        assert response.status_code == 200
        data = response.json()

        winner = data["winner"]
        rank_one = next(r for r in data["results"] if r["rank"] == 1)
        assert winner == rank_one["token"]["ticker"]

    def test_competition_market_share_sums_to_one(self, client):
        """Market shares sum to approximately 1."""
        response = client.post("/simulate/competition", json={
            "tokens": [
                {"name": "A", "ticker": "A", "narrative": "A"},
                {"name": "B", "ticker": "B", "narrative": "B"}
            ],
            "hours": 12
        })
        assert response.status_code == 200
        data = response.json()

        total_share = sum(r["market_share"] for r in data["results"])
        assert 0.99 <= total_share <= 1.01  # Allow small floating point error

    def test_competition_all_market_conditions(self, client):
        """Competition works with all market conditions."""
        conditions = ["bear", "crab", "bull", "euphoria"]
        for condition in conditions:
            response = client.post("/simulate/competition", json={
                "tokens": [
                    {"name": "A", "ticker": "A", "narrative": "A"},
                    {"name": "B", "ticker": "B", "narrative": "B"}
                ],
                "hours": 6,
                "market_condition": condition
            })
            assert response.status_code == 200, f"Condition {condition} failed"


class TestResponseFormat:
    """Tests for API response format consistency."""

    def test_simulation_response_structure(self, client):
        """Simulation response has complete structure."""
        response = client.post("/simulate", json={
            "token": {
                "name": "StructTest",
                "ticker": "STRUCT",
                "narrative": "Testing structure"
            },
            "hours": 12
        })
        assert response.status_code == 200
        data = response.json()

        # Required fields
        required = [
            "tweets", "viral_coefficient", "peak_sentiment",
            "sentiment_stability", "fud_resistance", "total_mentions",
            "total_engagement", "influencer_pickups", "hours_to_peak",
            "dominant_narrative", "top_fud_points", "predicted_outcome",
            "confidence"
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_tweet_response_structure(self, client):
        """Tweet response has complete structure."""
        response = client.post("/simulate", json={
            "token": {
                "name": "TweetStruct",
                "ticker": "TWST",
                "narrative": "Testing tweet structure"
            },
            "hours": 24
        })
        assert response.status_code == 200
        data = response.json()

        if len(data["tweets"]) > 0:
            tweet = data["tweets"][0]
            required = [
                "id", "author_name", "author_handle", "author_type",
                "content", "hour", "likes", "retweets", "replies", "sentiment"
            ]
            for field in required:
                assert field in tweet, f"Missing tweet field: {field}"
