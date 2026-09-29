from __future__ import annotations

import json


def build_prompt(
    issue_title: str,
    status_code: str,
    endpoint: str,
    request_id: str,
    request_context: str,
    logs: str,
    classification: dict,
    compact_retry: bool = False,
) -> str:
    evidence = {
        "issue_title": issue_title or "not provided",
        "status_code": status_code or "unknown",
        "endpoint": endpoint or "unknown",
        "request_id": request_id or "not provided",
        "request_context": request_context or "not provided",
        "logs": logs or "not provided",
        "deterministic_classifier": classification,
    }

    compact = """
IMPORTANT RETRY MODE:
Your previous output could not be parsed. Make this response compact.
Use at most 3 likely causes, 4 clarification questions, and 5 diagnostic steps.
""" if compact_retry else ""

    return f"""
You are an enterprise Claude API support copilot assisting a senior support engineer.

Analyze ONLY the incident evidence below. Your job is to produce a technically useful
support artifact, not a generic explanation.

GROUNDING RULES
- Treat supplied logs/status/request context as observations.
- Treat the deterministic classifier as a hint, not proof of root cause.
- Never invent account settings, quota values, customer architecture, headers, model
  availability, changes already attempted, or an outage.
- Do not claim the exact limiting dimension for a 429 unless the evidence proves it.
- If a cause is plausible but unconfirmed, label it as a hypothesis.
- A HIGH-confidence cause must cite concrete supplied evidence.
- If evidence is insufficient, say "insufficient evidence".
- Prefer reversible diagnostics before configuration changes.
- Never request API keys, bearer tokens, passwords, or secrets.
- Keep the customer response concise, calm, non-blaming, and action-oriented.
- Use the supplied request ID in escalation guidance when present.
- Do not diagnose customer intent or blame a user/team.

Return VALID JSON ONLY. No markdown fences and no prose outside the JSON.

Required schema:
{{
  "issue_summary": "1-3 concise sentences",
  "classification": {{
    "failure_domain": "string",
    "severity": "low|medium|high|critical",
    "retryable": true,
    "confidence": "low|medium|high"
  }},
  "evidence_used": ["specific observed fact"],
  "likely_causes": [
    {{
      "cause": "hypothesis stated without overclaiming",
      "confidence": "low|medium|high",
      "evidence": "specific supplied evidence or insufficient evidence",
      "disconfirming_signal": "what would make this cause less likely"
    }}
  ],
  "clarification_questions": ["targeted question"],
  "diagnostic_steps": [
    {{
      "step": 1,
      "action": "specific action",
      "why": "reason",
      "expected_signal": "what result confirms or rules out a hypothesis"
    }}
  ],
  "escalation_criteria": ["specific escalation condition"],
  "customer_response": "short customer-ready response",
  "escalation_summary": "concise internal handoff"
}}

{compact}

<incident_evidence>
{json.dumps(evidence, indent=2)}
</incident_evidence>
""".strip()
