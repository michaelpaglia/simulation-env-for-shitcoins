"""FastAPI application for shitcoin simulation."""

import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

from ..models.token import Token, MarketCondition, MemeStyle
from ..simulation.engine import SimulationEngine
from ..utils.twitter import TwitterClient, get_market_sentiment

load_dotenv()

app = FastAPI(
    title="Shitcoin Simulation API",
    description="Simulate how your token performs on CT before launch",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
engine = SimulationEngine(api_key=os.getenv("ANTHROPIC_API_KEY"))


# Request/Response Models
class TokenConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    ticker: str = Field(..., min_length=1, max_length=10)
    narrative: str = Field(..., min_length=1, max_length=500)
    tagline: Optional[str] = Field(default=None, max_length=100)
    meme_style: str = Field(default="absurd")
    market_condition: str = Field(default="crab")


class SimulationRequest(BaseModel):
    token: TokenConfig
    hours: int = Field(default=48, ge=1, le=168)
    use_twitter_priors: bool = Field(default=False)
    similar_tokens: Optional[list[str]] = Field(default=None)


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

    try:
        # Map string enums
        meme_style = MemeStyle(request.token.meme_style)
        market_condition = MarketCondition(request.token.market_condition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")

    # Optionally fetch Twitter priors to calibrate
    if request.use_twitter_priors and os.getenv("TWITTER_BEARER_TOKEN"):
        try:
            market_data = get_market_sentiment(request.similar_tokens)
            market_condition = MarketCondition(market_data["condition"])
        except Exception as e:
            print(f"Twitter prior fetch failed, using defaults: {e}")

    # Create token
    token = Token(
        name=request.token.name,
        ticker=request.token.ticker.upper(),
        narrative=request.token.narrative,
        tagline=request.token.tagline,
        meme_style=meme_style,
        market_condition=market_condition,
    )

    # Run simulation
    result = engine.run_simulation(token, hours=request.hours, verbose=False)

    # Get tweets from the simulation state (need to re-run to capture tweets)
    # For now, run a shorter sim to get tweet samples
    state = engine.run_simulation(token, hours=min(request.hours, 24), verbose=False)

    # Extract tweets from the last run
    # Since we return SimulationResult, we need to access the engine's internal state
    # Let's modify to capture tweets during simulation
    tweet_responses = []

    # Run simulation again with tweet capture
    from ..simulation.engine import SimulationState
    sim_state = SimulationState(token=token)

    # Seed
    from ..agents.personas import get_persona, PersonaType
    bot = get_persona(PersonaType.BOT)
    initial = engine._generate_tweet(bot, token, sim_state)
    engine._update_state(sim_state, [initial])

    # Run and capture tweets
    for hour in range(1, min(request.hours, 48)):
        active = engine._select_active_personas(sim_state)
        if not active:
            continue

        recent = sim_state.tweets[-5:] if sim_state.tweets else []
        context = "\n".join(f"@{t.author.handle}: {t.content}" for t in recent)

        new_tweets = [engine._generate_tweet(p, token, sim_state, context) for p in active]
        engine._update_state(sim_state, new_tweets)

        if sim_state.momentum < -0.7 and sim_state.awareness < 0.3 and hour > 12:
            break

    # Convert tweets to response format
    for t in sim_state.tweets[:50]:  # Limit to 50 tweets
        tweet_responses.append(TweetResponse(
            id=t.id,
            author_name=t.author.name,
            author_handle=t.author.handle,
            author_type=t.author.type.value,
            content=t.content,
            hour=t.hour,
            likes=t.likes,
            retweets=t.retweets,
            replies=t.replies,
            sentiment=t.sentiment,
        ))

    # Compile final results
    final_result = engine._compile_results(sim_state)

    return SimulationResponse(
        tweets=tweet_responses,
        viral_coefficient=final_result.viral_coefficient,
        peak_sentiment=final_result.peak_sentiment,
        sentiment_stability=final_result.sentiment_stability,
        fud_resistance=final_result.fud_resistance,
        total_mentions=final_result.total_mentions,
        total_engagement=final_result.total_engagement,
        influencer_pickups=final_result.influencer_pickups,
        hours_to_peak=final_result.hours_to_peak,
        hours_to_death=final_result.hours_to_death,
        dominant_narrative=final_result.dominant_narrative,
        top_fud_points=final_result.top_fud_points,
        predicted_outcome=final_result.predicted_outcome,
        confidence=final_result.confidence,
    )


@app.post("/simulate/stream")
async def stream_simulation(request: SimulationRequest):
    """Stream simulation tweets as they're generated using Server-Sent Events."""

    try:
        meme_style = MemeStyle(request.token.meme_style)
        market_condition = MarketCondition(request.token.market_condition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")

    # Optionally fetch Twitter priors
    if request.use_twitter_priors and os.getenv("TWITTER_BEARER_TOKEN"):
        try:
            market_data = get_market_sentiment(request.similar_tokens)
            market_condition = MarketCondition(market_data["condition"])
        except Exception as e:
            print(f"Twitter prior fetch failed, using defaults: {e}")

    token = Token(
        name=request.token.name,
        ticker=request.token.ticker.upper(),
        narrative=request.token.narrative,
        tagline=request.token.tagline,
        meme_style=meme_style,
        market_condition=market_condition,
    )

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
