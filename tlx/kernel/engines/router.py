"""RouterEngine — per-message tier selection with auto-escalation."""
from __future__ import annotations

from typing import Any

import structlog

from kernel.engine import Engine
from kernel.routing import RoutingConfig, RoutingDecision, TaskClassifier
from kernel.schema import EngineResponse, Message
from kernel.tools import Tool

logger = structlog.get_logger(__name__)


class RouterEngine:
    name = "router"

    def __init__(
        self,
        engines: dict[int, Engine],
        classifier: TaskClassifier,
        config: RoutingConfig,
        prompt_builder: Any | None = None,
    ) -> None:
        self._engines = engines
        self._classifier = classifier
        self._cfg = config
        self._prompt_builder = prompt_builder
        self.last_decision: RoutingDecision | None = None
        self._recent_tool_names: list[str] = []
        self.model = "router"

    async def respond(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
        max_tokens: int | None = None,
    ) -> EngineResponse:
        decision = self._classifier.classify(messages, self._recent_tool_names)
        self.last_decision = decision

        if self._prompt_builder is not None:
            context_hints = ["rag"] if "docs_query" in self._recent_tool_names else []
            system = self._prompt_builder.build(
                tier=decision.tier,
                context_hints=context_hints,
            )

        attempt_tier = decision.tier
        for attempt in range(self._cfg.max_escalations + 1):
            engine = self._engines.get(attempt_tier)
            if engine is None:
                attempt_tier = min(attempt_tier + 1, len(self._cfg.tiers) - 1)
                continue
            try:
                resp = await engine.respond(
                    messages, tools, system,
                    max_tokens=decision.max_tokens,
                )
            except Exception as exc:
                logger.warning("router_engine_error", tier=attempt_tier, error=str(exc))
                attempt_tier = min(attempt_tier + 1, len(self._cfg.tiers) - 1)
                continue

            if resp.stop_reason == "max_tokens" and attempt < self._cfg.max_escalations:
                next_tier = min(attempt_tier + 1, len(self._cfg.tiers) - 1)
                logger.info("router_escalate", from_tier=attempt_tier, to_tier=next_tier)
                self.last_decision = RoutingDecision(
                    tier=next_tier,
                    model=self._cfg.tiers[next_tier],
                    max_tokens=self._cfg.token_budgets.get(f"tier{next_tier}", 4096),
                    reason="escalated: max_tokens",
                    escalated_from=attempt_tier,
                )
                attempt_tier = next_tier
                continue

            self._recent_tool_names = [tc.name for tc in resp.tool_calls]
            return resp

        raise RuntimeError(
            f"RouterEngine: all escalation attempts exhausted from tier {decision.tier}"
        )
