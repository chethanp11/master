from __future__ import annotations

import re
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict

from core.agents.base import BaseAgent, agent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult
from products.ade.schemas.intent_frame import IntentFrame


class IntentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str = ""
    dataset: Optional[str] = None
    input_text: Optional[str] = None


@agent(
    name="intent_agent",
    purpose="Interprets user intent and extracts analysis requirements",
    capabilities=["natural_language_understanding", "intent_classification", "parameter_extraction"],
    cost_hint="MED",
)
class IntentAgent(BaseAgent):
    name = "intent_agent"
    description = "Interprets analyst intent into a structured frame for ADE."

    @staticmethod
    def _question_type(text: str) -> str:
        lowered = text.lower()
        if any(token in lowered for token in ("why", "root cause", "cause", "explain")):
            return "explain_drop"
        if any(token in lowered for token in ("anomaly", "outlier", "spike", "unexpected")):
            return "anomaly_investigation"
        if any(token in lowered for token in ("compare", "vs", "versus")):
            return "comparison"
        if any(token in lowered for token in ("trend", "over time", "growth")):
            return "trend_summary"
        return "summary"

    @staticmethod
    def _extract_metrics(text: str) -> List[str]:
        lowered = text.lower()
        metrics: List[str] = []
        mapping = [
            ("amount_inr", ("amount", "spend", "purchase", "transaction amount", "volume")),
            ("risk_score", ("risk", "risk score")),
            ("fraud_label", ("fraud", "chargeback", "suspicious")),
            ("decline_reason", ("decline", "rejection", "failed transactions")),
            ("value", ("value",)),
        ]
        for column, tokens in mapping:
            if any(token in lowered for token in tokens):
                metrics.append(column)
        match = re.search(r"\bh(\d{4})\b", lowered)
        if match:
            metrics.append(f"H{match.group(1)}")
        return metrics

    @staticmethod
    def _extract_entities(text: str) -> List[str]:
        lowered = text.lower()
        entities: List[str] = []
        if "branded_cards_transactions" in lowered or "branded cards" in lowered:
            entities.append("branded_cards_transactions")
        file_matches = re.findall(r"([\w\-]+\.csv)", lowered)
        for match in file_matches:
            entities.append(match)
        return entities

    @staticmethod
    def _extract_time_window(text: str) -> Optional[str]:
        lowered = text.lower()
        match = re.search(r"last\s+(\d+\s+\w+)", lowered)
        if match:
            return match.group(1)
        if "last quarter" in lowered:
            return "last quarter"
        if "last year" in lowered or "past year" in lowered:
            return "last year"
        return None

    @staticmethod
    def _requested_outputs(text: str) -> List[str]:
        lowered = text.lower()
        outputs: List[str] = []
        if any(token in lowered for token in ("chart", "plot", "graph", "visual")):
            outputs.append("chart")
        if "table" in lowered:
            outputs.append("table")
        if any(token in lowered for token in ("report", "summary", "narrative", "explain")):
            outputs.append("narrative")
        if not outputs:
            outputs.append("narrative")
        return outputs

    @staticmethod
    def _build_blocking_question(missing: List[str]) -> Optional[str]:
        if not missing:
            return None
        parts = []
        if "dataset" in missing:
            parts.append("the dataset to analyze (e.g., branded_cards_transactions)")
        if "metric" in missing:
            parts.append("the metric to focus on (e.g., amount_inr, risk_score)")
        if "time_window" in missing:
            parts.append("the time window (e.g., last 30 days)")
        detail = "; ".join(parts)
        return (
            "I need a bit more detail to proceed: "
            f"{detail}. This ensures the analysis is correct and scoped."
        )

    def run(self, step_context: Any) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            params = step_context.step.params if step_context.step else {}
            input_text = ""
            if isinstance(params, dict):
                input_text = str(params.get("input_text") or "").strip()
            if not input_text:
                input_text = str(
                    payload.get("intent")
                    or payload.get("prompt")
                    or payload.get("question")
                    or payload.get("instructions")
                    or ""
                ).strip()

            lowered = input_text.lower()
            inferred_entities = self._extract_entities(lowered)
            payload_dataset = payload.get("dataset")
            if payload_dataset and payload_dataset not in inferred_entities:
                inferred_entities.append(str(payload_dataset))
            inferred_metrics = self._extract_metrics(lowered)
            inferred_time_window = self._extract_time_window(lowered)

            missing: List[str] = []
            if not inferred_entities:
                missing.append("dataset")
            if not inferred_metrics:
                missing.append("metric")
            if not inferred_time_window:
                missing.append("time_window")

            blocking_question = self._build_blocking_question(missing) or "Provide any clarification needed."
            blocking_questions = [blocking_question] if missing else []

            confidence_score = 0.2 if missing else 0.75
            if confidence_score >= 0.7:
                confidence_label = "high"
            elif confidence_score >= 0.4:
                confidence_label = "medium"
            else:
                confidence_label = "low"

            frame = IntentFrame(
                intent_summary=input_text or "No intent provided.",
                inferred_entities=inferred_entities,
                inferred_metrics=inferred_metrics,
                inferred_time_window=inferred_time_window,
                requested_outputs=self._requested_outputs(lowered),
                confidence_score=confidence_score,
                confidence_label=confidence_label,
                blocking_required=bool(missing),
                blocking_questions=blocking_questions,
                blocking_question=blocking_question,
            )
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=frame.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> IntentAgent:
    return IntentAgent()
