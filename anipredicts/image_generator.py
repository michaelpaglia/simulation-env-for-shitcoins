"""
Grok/xAI Image Generator
Creates anime-style reaction images for trading signals
"""

import httpx
import os
import base64
from typing import Optional
from edge_detector import Edge


class GrokImageGenerator:
    API_URL = "https://api.x.ai/v1/images/generations"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY not provided")

    def _build_prompt(self, edge: Edge) -> str:
        """Generate appropriate anime character prompt based on edge type"""

        # Base style
        base_style = "anime art style, kawaii, cute anime girl, vibrant colors, digital art, high quality"

        # Reaction based on edge type and direction
        if edge.edge_type == "arbitrage":
            reaction = "excited anime girl with sparkling eyes, holding money, victorious pose, celebrating"
            mood = "ecstatic, winning"

        elif edge.edge_type == "odds_movement":
            if edge.direction == "YES":
                reaction = "confident anime girl pointing upward, smirking, bullish energy, rocket symbols in background"
                mood = "confident, bullish"
            else:
                reaction = "cautious anime girl looking down, contemplative expression, bear symbols"
                mood = "cautious, bearish"

        elif edge.edge_type == "volume_spike":
            reaction = "surprised anime girl with wide eyes, looking at a crowd of people rushing in, busy market scene"
            mood = "surprised, alert"

        elif edge.edge_type == "orderbook_imbalance":
            if edge.direction == "YES":
                reaction = "knowing anime girl with a sly smile, finger on lips, detective pose, magnifying glass"
                mood = "clever, knowing"
            else:
                reaction = "worried anime girl biting lip, looking at something falling, concerned expression"
                mood = "worried, cautious"

        else:
            reaction = "cute anime girl with questioning expression, looking at charts"
            mood = "curious"

        # Confidence affects intensity
        if edge.confidence == "high":
            intensity = "very expressive, dramatic lighting, emphasized emotions"
        elif edge.confidence == "medium":
            intensity = "moderately expressive, soft lighting"
        else:
            intensity = "subtle expression, gentle mood"

        prompt = f"{reaction}, {mood}, {intensity}, {base_style}, trading theme, prediction market aesthetic"

        return prompt

    async def generate_image(self, edge: Edge) -> Optional[bytes]:
        """Generate an anime reaction image for the given edge"""
        prompt = self._build_prompt(edge)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "grok-2-image-1212",
                        "prompt": prompt,
                        "n": 1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                # Extract image (could be URL or base64)
                if data.get("data") and len(data["data"]) > 0:
                    item = data["data"][0]

                    # Check for base64
                    if item.get("b64_json"):
                        return base64.b64decode(item["b64_json"])

                    # Check for URL - download it
                    if item.get("url"):
                        img_resp = await client.get(item["url"])
                        img_resp.raise_for_status()
                        return img_resp.content

                return None

            except httpx.HTTPStatusError as e:
                print(f"Grok API error: {e.response.status_code} - {e.response.text[:200]}")
                return None
            except Exception as e:
                print(f"Image generation failed: {e}")
                return None

    async def generate_and_save(self, edge: Edge, output_path: str) -> bool:
        """Generate image and save to file"""
        image_bytes = await self.generate_image(edge)

        if image_bytes:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return True

        return False
