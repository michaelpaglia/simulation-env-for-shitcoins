"""
LLM Feedback Loop System

Evaluate shitcoin concepts using synthetic CT simulation + LLM feedback.

Flow:
1. Real Twitter data -> trains priors (sentiment patterns, engagement norms)
2. Token concept -> input (name, ticker, narrative, hook)
3. Synthetic simulation -> generates fake CT reactions
4. LLM evaluates -> "narrative weak", "hook not viral", "FUD vulnerable"
5. Iterate -> refine concept before deploying

All simulation data is synthetic. Real data only informs priors.
"""

from .observer import SimulationObserver
from .analyzer import LLMAnalyzer
from .feedback_loop import FeedbackLoop
from .adjustments import AdjustmentEngine
from .token_evaluator import TokenEvaluator, TokenConcept, ConceptFeedback
from .ct_integration import CTConceptEvaluator, CTSimulationRunner

__all__ = [
    "SimulationObserver",
    "LLMAnalyzer",
    "FeedbackLoop",
    "AdjustmentEngine",
    "TokenEvaluator",
    "TokenConcept",
    "ConceptFeedback",
    "CTConceptEvaluator",
    "CTSimulationRunner",
]
