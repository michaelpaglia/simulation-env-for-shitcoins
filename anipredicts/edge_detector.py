"""
Edge Detection Engine
Identifies trading opportunities from Polymarket data
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from polymarket_client import Market, OrderBook, PolymarketClient


@dataclass
class Edge:
    market: Market
    edge_type: str  # "arbitrage", "odds_movement", "volume_spike", "orderbook_imbalance"
    description: str
    confidence: str  # "low", "medium", "high"
    magnitude: float  # how significant is the edge (0-100)
    direction: str  # "YES", "NO", or "NEUTRAL"
    detected_at: datetime

    def to_tweet_text(self) -> str:
        """Generate tweet text for this edge"""
        emoji_map = {
            "arbitrage": "free money alert",
            "odds_movement": "big move detected",
            "volume_spike": "money flowing in",
            "orderbook_imbalance": "smart money signal",
        }

        direction_emoji = "^" if self.direction == "YES" else "v" if self.direction == "NO" else "~"

        lines = [
            f"{emoji_map.get(self.edge_type, 'edge detected')}",
            f"",
            f"{self.market.question[:180]}",
            f"",
            f"{direction_emoji} {self.direction} @ {self.market.yes_price * 100:.0f}c" if self.direction == "YES"
                else f"{direction_emoji} {self.direction} @ {self.market.no_price * 100:.0f}c" if self.direction == "NO"
                else f"current: YES {self.market.yes_price * 100:.0f}c / NO {self.market.no_price * 100:.0f}c",
            f"",
            f"{self.description}",
            f"",
            f"polymarket.com/event/{self.market.slug}",
        ]
        return "\n".join(lines)


class EdgeDetector:
    def __init__(
        self,
        min_odds_change: float = 0.05,  # 5% minimum odds change
        min_volume_usd: float = 1000,   # minimum 24h volume
        arbitrage_threshold: float = 0.98,  # YES + NO < 98 cents = arb
    ):
        self.min_odds_change = min_odds_change
        self.min_volume_usd = min_volume_usd
        self.arbitrage_threshold = arbitrage_threshold
        self.price_history: dict[str, list[tuple[datetime, float, float]]] = {}

    def update_price(self, market: Market):
        """Track price over time for a market"""
        key = market.condition_id
        now = datetime.now()

        if key not in self.price_history:
            self.price_history[key] = []

        self.price_history[key].append((now, market.yes_price, market.no_price))

        # Keep only last 100 data points per market
        if len(self.price_history[key]) > 100:
            self.price_history[key] = self.price_history[key][-100:]

    def detect_arbitrage(self, market: Market) -> Optional[Edge]:
        """Check if YES + NO prices sum to less than $1"""
        total = market.yes_price + market.no_price

        if total < self.arbitrage_threshold:
            gap = (1 - total) * 100
            return Edge(
                market=market,
                edge_type="arbitrage",
                description=f"market mispriced - {gap:.1f}c gap detected! YES + NO = {total*100:.0f}c",
                confidence="high",
                magnitude=gap,
                direction="NEUTRAL",
                detected_at=datetime.now(),
            )
        return None

    def detect_odds_movement(self, market: Market) -> Optional[Edge]:
        """Detect significant price movement"""
        key = market.condition_id
        history = self.price_history.get(key, [])

        if len(history) < 2:
            return None

        # Compare to oldest recorded price
        oldest_time, oldest_yes, oldest_no = history[0]
        current_yes = market.yes_price
        current_no = market.no_price

        yes_change = current_yes - oldest_yes
        no_change = current_no - oldest_no

        # Check if movement exceeds threshold
        if abs(yes_change) >= self.min_odds_change:
            direction = "YES" if yes_change > 0 else "NO"
            change_pct = abs(yes_change) * 100

            return Edge(
                market=market,
                edge_type="odds_movement",
                description=f"{'pumping' if yes_change > 0 else 'dumping'} - YES moved {'+' if yes_change > 0 else ''}{yes_change*100:.1f}c in recent checks",
                confidence="medium" if change_pct < 10 else "high",
                magnitude=change_pct,
                direction=direction,
                detected_at=datetime.now(),
            )
        return None

    def detect_volume_spike(self, market: Market, avg_volume: float = 5000) -> Optional[Edge]:
        """Detect unusual volume activity"""
        if market.volume_24h > avg_volume * 3:  # 3x average volume
            spike_factor = market.volume_24h / avg_volume

            return Edge(
                market=market,
                edge_type="volume_spike",
                description=f"volume spike! ${market.volume_24h:,.0f} in 24h ({spike_factor:.1f}x normal)",
                confidence="medium",
                magnitude=min(spike_factor * 10, 100),
                direction="NEUTRAL",
                detected_at=datetime.now(),
            )
        return None

    def detect_orderbook_imbalance(
        self, market: Market, orderbook: Optional[OrderBook]
    ) -> Optional[Edge]:
        """Detect significant bid/ask imbalance suggesting directional pressure"""
        if not orderbook or not orderbook.bids or not orderbook.asks:
            return None

        # Sum up volume on each side (top 5 levels)
        bid_volume = sum(b.size for b in orderbook.bids[:5])
        ask_volume = sum(a.size for a in orderbook.asks[:5])

        if bid_volume == 0 or ask_volume == 0:
            return None

        ratio = bid_volume / ask_volume

        # Strong buy pressure: bids >> asks
        if ratio > 3.0:
            return Edge(
                market=market,
                edge_type="orderbook_imbalance",
                description=f"heavy buy pressure - {ratio:.1f}x more bids than asks. whales loading?",
                confidence="medium",
                magnitude=min(ratio * 15, 100),
                direction="YES",
                detected_at=datetime.now(),
            )

        # Strong sell pressure: asks >> bids
        if ratio < 0.33:
            return Edge(
                market=market,
                edge_type="orderbook_imbalance",
                description=f"heavy sell pressure - {1/ratio:.1f}x more asks than bids. insiders selling?",
                confidence="medium",
                magnitude=min((1/ratio) * 15, 100),
                direction="NO",
                detected_at=datetime.now(),
            )

        return None

    async def scan_market(
        self, market: Market, client: PolymarketClient
    ) -> list[Edge]:
        """Run all detection strategies on a single market"""
        edges = []

        # Skip low-volume markets
        if market.volume_24h < self.min_volume_usd:
            return edges

        # Update price tracking
        self.update_price(market)

        # Run detection strategies
        arb = self.detect_arbitrage(market)
        if arb:
            edges.append(arb)

        movement = self.detect_odds_movement(market)
        if movement:
            edges.append(movement)

        volume = self.detect_volume_spike(market)
        if volume:
            edges.append(volume)

        # Fetch orderbook for imbalance detection
        orderbook = await client.get_orderbook(market.yes_token_id)
        imbalance = self.detect_orderbook_imbalance(market, orderbook)
        if imbalance:
            edges.append(imbalance)

        return edges

    async def scan_all_markets(
        self, client: PolymarketClient, limit: int = 50
    ) -> list[Edge]:
        """Scan top markets for edges"""
        all_edges = []

        markets = await client.get_markets(limit=limit)

        for market in markets:
            edges = await self.scan_market(market, client)
            all_edges.extend(edges)

        # Sort by magnitude (most significant first)
        all_edges.sort(key=lambda e: e.magnitude, reverse=True)

        return all_edges
