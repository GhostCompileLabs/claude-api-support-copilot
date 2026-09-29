from __future__ import annotations

import json
import re
from typing import Any


REQUIRED_KEYS = {
    "issue_summary",
    "classification",
    "evidence_used",
    "likely_causes",
    "clarification_questions",
    "diagnostic_steps",
    "escalation_criteria",
    "customer_response",
    "escalation_summary",
}

ALLOWED_SEVERITY = {"low", "medium", "high", "critical"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}


def _extract_json(text: str) -> str:
    value = (text or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value)
        value = re.sub(r"\s*```$", "", value)
    # Defensive extraction in case a model adds text around the JSON object.
    start = value.find("{")
    end = value.rfind("}")
    if start >= 0 and end > start:
        value = value[start:end + 1]
    return value.strip()


def validate_model_output(text: str) -> tuple[bool, dict[str, Any] | None, str]:
    try:
        data = json.loads(_extract_json(text))
    except json.JSONDecodeError as exc:
        return False, None, f"Claude returned invalid JSON: {exc}"

    if not isinstance(data, dict):
        return False, None, "Claude output was not a JSON object."

    missing = sorted(REQUIRED_KEYS - set(data.keys()))
    if missing:
        return False, None, f"Claude output was missing fields: {', '.join(missing)}"

    cls = data.get("classification")
    if not isinstance(cls, dict):
        return False, None, "classification must be an object."

    if cls.get("severity") not in ALLOWED_SEVERITY:
        return False, None, "classification.severity is invalid."

    if cls.get("confidence") not in ALLOWED_CONFIDENCE:
        return False, None, "classification.confidence is invalid."

    if not isinstance(cls.get("retryable"), bool):
        return False, None, "classification.retryable must be boolean."

    causes = data.get("likely_causes")
    if not isinstance(causes, list):
        return False, None, "likely_causes must be a list."

    for item in causes:
        if not isinstance(item, dict):
            return False, None, "Every likely cause must be an object."
        confidence = item.get("confidence")
        evidence = str(item.get("evidence", "")).strip().lower()
        if confidence not in ALLOWED_CONFIDENCE:
            return False, None, "A likely cause contains an invalid confidence value."
        if confidence == "high" and (not evidence or evidence == "insufficient evidence"):
            return False, None, "A high-confidence cause must cite concrete evidence."

    steps = data.get("diagnostic_steps")
    if not isinstance(steps, list) or not steps:
        return False, None, "diagnostic_steps must be a non-empty list."

    if len(steps) > 8:
        return False, None, "diagnostic_steps is too long."

    customer_response = str(data.get("customer_response", "")).strip()
    if not customer_response:
        return False, None, "customer_response must not be empty."

    return True, data, ""
