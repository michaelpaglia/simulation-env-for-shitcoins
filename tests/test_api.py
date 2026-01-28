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
        """Invalid meme style returns error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test",
                "meme_style": "invalid_style"
            }
        })
        assert response.status_code == 400

    def test_simulate_invalid_market_condition(self, client):
        """Invalid market condition returns error."""
        response = client.post("/simulate", json={
            "token": {
                "name": "Test",
                "ticker": "TEST",
                "narrative": "Test",
                "market_condition": "super_bull"
            }
        })
        assert response.status_code == 400

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
