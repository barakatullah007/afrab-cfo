from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PlannerExecutionContext:
    """Mutable execution context passed between planner steps."""

    user_question: str
    detected_goal: str
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    executed_tools: set[str] = field(default_factory=set)
    tool_outputs: dict[str, Any] = field(default_factory=dict)
    advisor_outputs: dict[str, Any] = field(default_factory=dict)
    execution_order: list[str] = field(default_factory=list)
    step_timestamps: dict[str, str] = field(default_factory=dict)
    llm_latency_ms: int | None = None
    _started_perf: float = field(default_factory=time.perf_counter)

    def has_tool_output(
        self,
        tool_name: str,
    ) -> bool:
        return tool_name in self.tool_outputs

    def add_tool_output(
        self,
        tool_name: str,
        output: Any,
    ) -> None:
        self.executed_tools.add(tool_name)
        self.tool_outputs[tool_name] = output
        self._mark_step(tool_name)

    def add_advisor_output(
        self,
        advisor_name: str,
        output: Any,
    ) -> None:
        self.advisor_outputs[advisor_name] = output
        self._mark_step(advisor_name)

    def execution_time_ms(self) -> int:
        return int((time.perf_counter() - self._started_perf) * 1000)

    def to_llm_payload(self) -> dict[str, Any]:
        return {
            "user_question": self.user_question,
            "detected_goal": self.detected_goal,
            "started_at": self.started_at.isoformat(),
            "execution_order": self.execution_order,
            "timestamps": self.step_timestamps,
            "tool_outputs": self.tool_outputs,
            "advisor_outputs": self.advisor_outputs,
        }

    def _mark_step(
        self,
        step_name: str,
    ) -> None:
        if step_name not in self.execution_order:
            self.execution_order.append(step_name)
        self.step_timestamps[step_name] = datetime.now(timezone.utc).isoformat()
