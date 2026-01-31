"""FastAPI application for shitcoin simulation."""

import os
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

from ..models.token import Token, MarketCondition, MemeStyle
from ..simulation.engine import SimulationEngine
from ..utils.twitter import TwitterClient, get_market_sentiment
from .harness_routes import router as harness_router
from .stake_routes import router as stake_router

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shitcoin Simulation API",
    description="Simulate how your token performs on CT before launch",
    version="0.1.0",
)

# CORS for frontend - allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include harness routes
app.include_router(harness_router)

# Include stake routes
app.include_router(stake_router)


# Stake verification (enabled via env var)
REQUIRE_STAKE = os.getenv("REQUIRE_STAKE_VERIFICATION", "false").lower() == "true"


async def verify_stake_if_required(
    wallet: Optional[str],
    stake_pda: Optional[str],
    required_hours: int,
) -> Optional[int]:
    """Verify stake if required, returns allowed sim hours or raises HTTPException.

    Returns None if stake verification is disabled or not provided.
    Returns allowed hours if stake is valid.
    Raises HTTPException if stake is invalid.
    """
    if not REQUIRE_STAKE:
        return None

    if not wallet or not stake_pda:
        if REQUIRE_STAKE:
            raise HTTPException(
                status_code=402,
                detail="Stake verification required. Provide wallet and stake_pda.",
            )
        return None

    from ..solana import StakeVerifier

    verifier = StakeVerifier()
    result = await verifier.verify_stake(wallet, stake_pda)

    if not result.valid:
        raise HTTPException(
            status_code=402,
            detail=f"Invalid stake: {result.message}",
        )

    # Verify stake tier supports requested hours
    if result.sim_hours and required_hours > result.sim_hours:
        raise HTTPException(
            status_code=402,
            detail=f"Stake tier only allows {result.sim_hours}h simulations, requested {required_hours}h",
        )

    return result.sim_hours


def get_engine() -> SimulationEngine:
    """Create a SimulationEngine instance for this request.

    Each request gets its own engine instance to ensure thread safety
    when handling concurrent requests from multiple users.
    """
    return SimulationEngine(api_key=os.getenv("ANTHROPIC_API_KEY"))


# Request/Response Models
class TokenConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    ticker: str = Field(..., min_length=1, max_length=10)
    narrative: str = Field(..., min_length=1, max_length=500)
    tagline: Optional[str] = Field(default=None, max_length=100)
    meme_style: MemeStyle = Field(default=MemeStyle.ABSURD)
    market_condition: MarketCondition = Field(default=MarketCondition.CRAB)


class SimulationRequest(BaseModel):
    token: TokenConfig
    hours: int = Field(default=48, ge=1, le=168)
    use_twitter_priors: bool = Field(default=False)
    similar_tokens: Optional[list[str]] = Field(default=None)
    # On-chain stake verification (optional)
    wallet: Optional[str] = Field(default=None, description="Wallet public key for stake verification")
    stake_pda: Optional[str] = Field(default=None, description="Stake account PDA address")


class TweetResponse(BaseModel):
    id: str
    author_name: str
    author_handle: str
    author_type: str
    content: str
    hour: int
    likes: int
    retweets: int
    replies: int
    sentiment: float
    # Interaction fields
    tweet_type: str = "original"
    is_reply_to: Optional[str] = None
    quotes_tweet: Optional[str] = None
    thread_depth: int = 0
    # Denormalized for UI display
    reply_to_author: Optional[str] = None
    quoted_content: Optional[str] = None
    quoted_author: Optional[str] = None


class SimulationResponse(BaseModel):
    tweets: list[TweetResponse]
    viral_coefficient: float
    peak_sentiment: float
    sentiment_stability: float
    fud_resistance: float
    total_mentions: int
    total_engagement: int
    influencer_pickups: int
    hours_to_peak: int
    hours_to_death: Optional[int]
    dominant_narrative: str
    top_fud_points: list[str]
    predicted_outcome: str
    confidence: float


class MarketSentimentResponse(BaseModel):
    sentiment: float
    condition: str
    tweet_count: Optional[int] = None


class TwitterPriorResponse(BaseModel):
    query: str
    tweet_count: int
    avg_sentiment: float
    engagement_rate: float
    top_accounts: list[str]
    common_phrases: list[str]


@app.get("/")
async def root():
    return {"status": "ok", "message": "Shitcoin Simulation API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """Run a full simulation for a token."""

    # Verify stake if required
    await verify_stake_if_required(request.wallet, request.stake_pda, request.hours)

    # Enums are already validated by Pydantic, just extract values
    meme_style = request.token.meme_style
    market_condition = request.token.market_condition

    # Optionally fetch Twitter priors to calibrate
    if request.use_twitter_priors and os.getenv("TWITTER_BEARER_TOKEN"):
        try:
            market_data = get_market_sentiment(request.similar_tokens)
            market_condition = MarketCondition(market_data["condition"])
        except Exception as e:
            logger.warning(f"Twitter prior fetch failed, using defaults: {e}")

    # Create token
    token = Token(
        name=request.token.name,
        ticker=request.token.ticker.upper(),
        narrative=request.token.narrative,
        tagline=request.token.tagline,
        meme_style=meme_style,
        market_condition=market_condition,
    )

    # Create per-request engine instance for thread safety
    engine = get_engine()

    # Run simulation ONCE using streaming to capture both tweets and results
    tweet_responses: list[TweetResponse] = []
    final_result = None

    for event in engine.run_simulation_stream(token, hours=request.hours):
        if event["type"] == "tweet":
            tweet = event["tweet"]
            # Only keep first 50 tweets
            if len(tweet_responses) < 50:
                tweet_responses.append(TweetResponse(
                    id=tweet["id"],
                    author_name=tweet["author_name"],
                    author_handle=tweet["author_handle"],
                    author_type=tweet["author_type"],
                    content=tweet["content"],
                    hour=tweet["hour"],
                    likes=tweet["likes"],
                    retweets=tweet["retweets"],
                    replies=tweet["replies"],
                    sentiment=tweet["sentiment"],
                    tweet_type=tweet.get("tweet_type", "original"),
                    is_reply_to=tweet.get("is_reply_to"),
                    quotes_tweet=tweet.get("quotes_tweet"),
                    thread_depth=tweet.get("thread_depth", 0),
                    reply_to_author=tweet.get("reply_to_author"),
                    quoted_content=tweet.get("quoted_content"),
                    quoted_author=tweet.get("quoted_author"),
                ))
        elif event["type"] == "result":
            final_result = event["result"]

    if final_result is None:
        raise HTTPException(status_code=500, detail="Simulation did not produce results")

    return SimulationResponse(
        tweets=tweet_responses,
        viral_coefficient=final_result["viral_coefficient"],
        peak_sentiment=final_result["peak_sentiment"],
        sentiment_stability=final_result["sentiment_stability"],
        fud_resistance=final_result["fud_resistance"],
        total_mentions=final_result["total_mentions"],
        total_engagement=final_result["total_engagement"],
        influencer_pickups=final_result["influencer_pickups"],
        hours_to_peak=final_result["hours_to_peak"],
        hours_to_death=final_result["hours_to_death"],
        dominant_narrative=final_result["dominant_narrative"],
        top_fud_points=final_result["top_fud_points"],
        predicted_outcome=final_result["predicted_outcome"],
        confidence=final_result["confidence"],
    )


@app.post("/simulate/stream")
async def stream_simulation(request: SimulationRequest):
    """Stream simulation tweets as they're generated using Server-Sent Events."""

    # Verify stake if required
    await verify_stake_if_required(request.wallet, request.stake_pda, request.hours)

    # Enums are already validated by Pydantic
    meme_style = request.token.meme_style
    market_condition = request.token.market_condition

    # Optionally fetch Twitter priors
    if request.use_twitter_priors and os.getenv("TWITTER_BEARER_TOKEN"):
        try:
            market_data = get_market_sentiment(request.similar_tokens)
            market_condition = MarketCondition(market_data["condition"])
        except Exception as e:
            logger.warning(f"Twitter prior fetch failed, using defaults: {e}")

    token = Token(
        name=request.token.name,
        ticker=request.token.ticker.upper(),
        narrative=request.token.narrative,
        tagline=request.token.tagline,
        meme_style=meme_style,
        market_condition=market_condition,
    )

    # Create per-request engine instance for thread safety
    engine = get_engine()

    async def event_generator():
        """Generate SSE events from simulation."""
        try:
            for event in engine.run_simulation_stream(token, hours=request.hours):
                # Format as SSE
                data = json.dumps(event)
                yield f"data: {data}\n\n"

                # Small delay to allow client to process
                await asyncio.sleep(0.05)

            # Send done event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Simulation stream error: {e}")
            error_event = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {error_event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/market-sentiment", response_model=MarketSentimentResponse)
async def market_sentiment(tokens: Optional[str] = None):
    """Get current CT market sentiment."""

    if not os.getenv("TWITTER_BEARER_TOKEN"):
        # Return default if no Twitter access
        return MarketSentimentResponse(sentiment=0.0, condition="crab")

    try:
        token_list = tokens.split(",") if tokens else None
        data = get_market_sentiment(token_list)
        return MarketSentimentResponse(
            sentiment=data["sentiment"],
            condition=data["condition"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sentiment: {e}")


@app.get("/twitter-prior", response_model=TwitterPriorResponse)
async def twitter_prior(token: str, similar: Optional[str] = None):
    """Get Twitter sentiment data for a token to calibrate simulation."""

    if not os.getenv("TWITTER_BEARER_TOKEN"):
        raise HTTPException(status_code=503, detail="Twitter API not configured")

    try:
        client = TwitterClient()
        similar_list = similar.split(",") if similar else None
        prior = client.get_sentiment_prior(token, similar_list)

        return TwitterPriorResponse(
            query=prior.query,
            tweet_count=prior.tweet_count,
            avg_sentiment=prior.avg_sentiment,
            engagement_rate=prior.engagement_rate,
            top_accounts=prior.top_accounts,
            common_phrases=prior.common_phrases,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prior: {e}")


@app.get("/personas")
async def list_personas():
    """List available simulation personas."""

    from ..agents.personas import PERSONAS, KOLS

    personas = []
    for p in PERSONAS.values():
        personas.append({
            "type": p.type.value,
            "name": p.name,
            "handle": p.handle,
            "influence_score": p.influence_score,
        })

    for p in KOLS:
        personas.append({
            "type": p.type.value,
            "name": p.name,
            "handle": p.handle,
            "influence_score": p.influence_score,
        })

    return {"personas": personas}
