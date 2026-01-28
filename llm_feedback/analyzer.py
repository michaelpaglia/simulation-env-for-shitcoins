"""
LLM Analyzer Module

Uses an LLM to analyze SYNTHETIC simulation state and provide insights.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional
import json

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


@dataclass
class Analysis:
    """Result of LLM analysis."""
    observations: list[str]
    concerns: list[str]
    recommendations: list[dict[str, Any]]
    reasoning: str
    confidence: float
    raw_response: str

    def has_recommendations(self) -> bool:
        return len(self.recommendations) > 0

    def to_dict(self) -> dict:
        return {
            "observations": self.observations,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
        }


DEFAULT_SYSTEM_PROMPT = """You are an expert simulation analyst. Your job is to observe a SYNTHETIC simulation and provide actionable feedback.

When analyzing simulation state, you should:
1. Identify patterns and trends in the metrics
2. Spot anomalies or concerning behaviors
3. Suggest specific parameter adjustments if needed
4. Explain your reasoning clearly

Respond in JSON format:
{
    "observations": ["observation 1", "observation 2", ...],
    "concerns": ["concern 1", ...],
    "recommendations": [
        {"parameter": "param_name", "current": value, "suggested": value, "reason": "why"}
    ],
    "reasoning": "Your detailed reasoning here",
    "confidence": 0.0 to 1.0
}

Be concise but thorough. Only recommend changes when you see clear evidence they would help."""


class LLMAnalyzer:
    """Analyzes synthetic simulation state using an LLM."""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None,
    ):
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        self.analysis_history: list[Analysis] = []

    @property
    def client(self):
        if self._client is None:
            if Anthropic is None:
                raise ImportError("anthropic package not installed")
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    def analyze(self, context: str, additional_prompt: str = "") -> Analysis:
        """Analyze simulation state and return structured analysis."""
        import time

        user_message = f"""Analyze this SYNTHETIC simulation state:

{context}

{additional_prompt}

Provide your analysis in JSON format."""

        # Retry with backoff for rate limits
        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                raw_response = response.content[0].text
                analysis = self._parse_response(raw_response)
                self.analysis_history.append(analysis)
                return analysis
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                # Return fallback on error
                return Analysis(
                    observations=["Analysis unavailable - rate limited"],
                    concerns=[],
                    recommendations=[],
                    reasoning=str(e),
                    confidence=0.0,
                    raw_response=str(e),
                )

    def _parse_response(self, response: str) -> Analysis:
        """Parse LLM response into Analysis structure."""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return Analysis(
                    observations=data.get("observations", []),
                    concerns=data.get("concerns", []),
                    recommendations=data.get("recommendations", []),
                    reasoning=data.get("reasoning", ""),
                    confidence=data.get("confidence", 0.5),
                    raw_response=response,
                )
        except json.JSONDecodeError:
            pass

        return Analysis([], [], [], response, 0.0, response)
