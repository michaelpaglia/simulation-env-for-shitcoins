"""Twitter API integration for fetching real CT sentiment."""

import os
import re
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TweetData:
    """Raw tweet data from Twitter API."""
    id: str
    text: str
    author_username: str
    author_name: str
    created_at: datetime
    likes: int
    retweets: int
    replies: int


@dataclass
class SentimentPrior:
    """Sentiment data from real tweets to calibrate simulation."""
    query: str
    tweet_count: int
    avg_sentiment: float
    engagement_rate: float
    top_accounts: list[str]
    common_phrases: list[str]
    sample_tweets: list[TweetData]


class TwitterClient:
    """Client for fetching Twitter data to calibrate simulations."""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("Twitter bearer token not found")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.bearer_token}"}

    def search_recent(
        self,
        query: str,
        max_results: int = 100,
        hours_back: int = 24
    ) -> list[TweetData]:
        """Search recent tweets matching a query."""

        # Add crypto-specific filters
        full_query = f"{query} -is:retweet lang:en"

        params = {
            "query": full_query,
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics",
            "user.fields": "username,name",
            "expansions": "author_id",
        }

        response = requests.get(
            f"{self.BASE_URL}/tweets/search/recent",
            headers=self._headers(),
            params=params
        )

        if response.status_code != 200:
            print(f"Twitter API error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        tweets = data.get("data", [])
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}

        results = []
        for tweet in tweets:
            author = users.get(tweet["author_id"], {})
            metrics = tweet.get("public_metrics", {})

            results.append(TweetData(
                id=tweet["id"],
                text=tweet["text"],
                author_username=author.get("username", "unknown"),
                author_name=author.get("name", "Unknown"),
                created_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                likes=metrics.get("like_count", 0),
                retweets=metrics.get("retweet_count", 0),
                replies=metrics.get("reply_count", 0),
            ))

        return results

    def get_sentiment_prior(self, token_name: str, similar_tokens: list[str] = None) -> SentimentPrior:
        """
        Get sentiment data for a token or similar tokens to calibrate simulation.

        Args:
            token_name: The token we're simulating
            similar_tokens: List of similar existing tokens to analyze
        """

        # Build search query
        queries = [f"${token_name}"]
        if similar_tokens:
            queries.extend([f"${t}" for t in similar_tokens[:3]])

        all_tweets = []
        for q in queries:
            tweets = self.search_recent(q, max_results=50)
            all_tweets.extend(tweets)

        if not all_tweets:
            return SentimentPrior(
                query=token_name,
                tweet_count=0,
                avg_sentiment=0.0,
                engagement_rate=0.0,
                top_accounts=[],
                common_phrases=[],
                sample_tweets=[],
            )

        # Calculate metrics
        total_engagement = sum(t.likes + t.retweets + t.replies for t in all_tweets)
        avg_engagement = total_engagement / len(all_tweets) if all_tweets else 0

        # Simple sentiment from keywords
        positive_words = ["moon", "pump", "bullish", "gem", "lfg", "wagmi", "based", "alpha"]
        negative_words = ["rug", "scam", "dump", "bearish", "ngmi", "dead", "sell"]

        sentiments = []
        for tweet in all_tweets:
            text_lower = tweet.text.lower()
            pos = sum(1 for w in positive_words if w in text_lower)
            neg = sum(1 for w in negative_words if w in text_lower)
            if pos + neg > 0:
                sentiments.append((pos - neg) / (pos + neg))
            else:
                sentiments.append(0)

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Top accounts by engagement
        account_engagement = {}
        for tweet in all_tweets:
            eng = tweet.likes + tweet.retweets
            account_engagement[tweet.author_username] = account_engagement.get(tweet.author_username, 0) + eng

        top_accounts = sorted(account_engagement.keys(), key=lambda x: account_engagement[x], reverse=True)[:5]

        # Common phrases (simple extraction)
        common_phrases = self._extract_common_phrases(all_tweets)

        return SentimentPrior(
            query=token_name,
            tweet_count=len(all_tweets),
            avg_sentiment=avg_sentiment,
            engagement_rate=avg_engagement,
            top_accounts=top_accounts,
            common_phrases=common_phrases,
            sample_tweets=sorted(all_tweets, key=lambda t: t.likes + t.retweets, reverse=True)[:5],
        )

    def _extract_common_phrases(self, tweets: list[TweetData]) -> list[str]:
        """Extract commonly used phrases from tweets."""
        # Simple word frequency
        word_count = {}
        for tweet in tweets:
            words = re.findall(r'\b\w+\b', tweet.text.lower())
            for word in words:
                if len(word) > 3 and word not in ["http", "https", "this", "that", "with"]:
                    word_count[word] = word_count.get(word, 0) + 1

        return sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)[:10]


def get_market_sentiment(tokens: list[str] = None) -> dict:
    """
    Get overall CT sentiment for calibrating market conditions.

    Args:
        tokens: Specific tokens to check, or None for general market
    """
    try:
        client = TwitterClient()

        if tokens:
            priors = [client.get_sentiment_prior(t) for t in tokens[:3]]
            avg_sentiment = sum(p.avg_sentiment for p in priors) / len(priors) if priors else 0
        else:
            # Check general crypto sentiment
            general = client.search_recent("crypto OR solana OR memecoin", max_results=100)
            if general:
                positive = ["bullish", "pump", "moon", "up"]
                negative = ["bearish", "dump", "down", "crash"]
                sentiments = []
                for t in general:
                    text = t.text.lower()
                    pos = sum(1 for w in positive if w in text)
                    neg = sum(1 for w in negative if w in text)
                    if pos + neg > 0:
                        sentiments.append((pos - neg) / (pos + neg))
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            else:
                avg_sentiment = 0

        # Map to market condition
        if avg_sentiment > 0.5:
            condition = "euphoria"
        elif avg_sentiment > 0.2:
            condition = "bull"
        elif avg_sentiment < -0.3:
            condition = "bear"
        else:
            condition = "crab"

        return {
            "sentiment": avg_sentiment,
            "condition": condition,
        }
    except Exception as e:
        print(f"Error fetching market sentiment: {e}")
        return {"sentiment": 0, "condition": "crab"}
