"""
Adjustment Engine Module

Applies LLM-recommended changes to SYNTHETIC simulation parameters.
Includes safety checks and rollback capabilities.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime
import copy


@dataclass
class Adjustment:
    """Record of a parameter adjustment."""
    timestamp: datetime
    parameter: str
    old_value: Any
    new_value: Any
    reason: str
    applied: bool = False
    rolled_back: bool = False


@dataclass
class AdjustmentConstraint:
    """Defines valid range/values for a parameter."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[list[Any]] = None
    max_change_per_tick: Optional[float] = None


class AdjustmentEngine:
    """
    Safely applies parameter adjustments to a SYNTHETIC simulation.

    Features:
    - Parameter constraints (min/max, allowed values)
    - Rate limiting on changes
    - Full history with rollback capability
    """

    def __init__(
        self,
        param_getter: Callable[[str], Any],
        param_setter: Callable[[str, Any], None],
        constraints: Optional[dict[str, AdjustmentConstraint]] = None,
    ):
        self.param_getter = param_getter
        self.param_setter = param_setter
        self.constraints = constraints or {}
        self.history: list[Adjustment] = []
        self.on_before_adjust: Optional[Callable[[Adjustment], bool]] = None
        self.on_after_adjust: Optional[Callable[[Adjustment], None]] = None

    def add_constraint(self, param: str, constraint: AdjustmentConstraint):
        self.constraints[param] = constraint

    def validate_adjustment(self, param: str, new_value: Any) -> tuple[bool, str]:
        if param not in self.constraints:
            return True, "No constraints defined"

        constraint = self.constraints[param]
        current = self.param_getter(param)

        if constraint.min_value is not None and new_value < constraint.min_value:
            return False, f"Value {new_value} below minimum {constraint.min_value}"
        if constraint.max_value is not None and new_value > constraint.max_value:
            return False, f"Value {new_value} above maximum {constraint.max_value}"

        if constraint.allowed_values is not None:
            if new_value not in constraint.allowed_values:
                return False, f"Value {new_value} not in allowed values"

        if constraint.max_change_per_tick is not None:
            if isinstance(current, (int, float)) and isinstance(new_value, (int, float)):
                change = abs(new_value - current)
                if change > constraint.max_change_per_tick:
                    return False, f"Change {change} exceeds max rate {constraint.max_change_per_tick}"

        return True, "Valid"

    def apply(self, param: str, new_value: Any, reason: str = "") -> tuple[bool, str]:
        current = self.param_getter(param)

        is_valid, validation_msg = self.validate_adjustment(param, new_value)
        if not is_valid:
            return False, f"Validation failed: {validation_msg}"

        adjustment = Adjustment(
            timestamp=datetime.now(),
            parameter=param,
            old_value=copy.deepcopy(current),
            new_value=new_value,
            reason=reason,
        )

        if self.on_before_adjust and not self.on_before_adjust(adjustment):
            return False, "Blocked by before_adjust hook"

        try:
            self.param_setter(param, new_value)
            adjustment.applied = True
            self.history.append(adjustment)
        except Exception as e:
            return False, f"Failed to apply: {str(e)}"

        if self.on_after_adjust:
            self.on_after_adjust(adjustment)

        return True, f"Applied: {param} changed from {current} to {new_value}"

    def apply_recommendations(
        self,
        recommendations: list[dict[str, Any]],
        confidence_threshold: float = 0.5,
        analysis_confidence: float = 1.0,
    ) -> list[tuple[str, bool, str]]:
        results = []

        if analysis_confidence < confidence_threshold:
            return [("*", False, f"Analysis confidence {analysis_confidence} below threshold")]

        for rec in recommendations:
            param = rec.get("parameter")
            new_value = rec.get("suggested")
            reason = rec.get("reason", "LLM recommendation")

            if not param or new_value is None:
                results.append((str(rec), False, "Invalid recommendation format"))
                continue

            success, msg = self.apply(param, new_value, reason)
            results.append((param, success, msg))

        return results

    def rollback(self, steps: int = 1) -> list[tuple[str, bool, str]]:
        results = []
        to_rollback = [a for a in reversed(self.history) if a.applied and not a.rolled_back][:steps]

        for adjustment in to_rollback:
            try:
                self.param_setter(adjustment.parameter, adjustment.old_value)
                adjustment.rolled_back = True
                results.append((adjustment.parameter, True, f"Rolled back to {adjustment.old_value}"))
            except Exception as e:
                results.append((adjustment.parameter, False, f"Rollback failed: {str(e)}"))

        return results
