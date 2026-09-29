from __future__ import annotations

from typing import Any

from classifier import classify_incident
from claude_client import ClaudeSupportClient
from prompt_builder import build_prompt
from sanitizer import sanitize
from validator import validate_model_output


def _fallback_report(
    issue_title: str,
    request_id: str,
    classification: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    checks = classification["recommended_checks"]
    evidence = classification["evidence"]

    return {
        "issue_summary": issue_title or "Claude API incident",
        "classification": {
            "failure_domain": classification["category"],
            "severity": classification["severity"],
            "retryable": classification["retryable"],
            "confidence": "medium" if classification["category"] != "unknown" else "low",
        },
        "evidence_used": evidence,
        "likely_causes": [
            {
                "cause": f"Evidence is consistent with the {classification['category']} failure domain.",
                "confidence": "medium" if classification["category"] != "unknown" else "low",
                "evidence": "; ".join(evidence),
                "disconfirming_signal": "A minimal reproduction returns a different error class or status.",
            }
        ],
        "clarification_questions": [
            "Does the issue reproduce with a minimal request?",
            "When did the issue begin, and is it intermittent or consistent?",
            "What changed immediately before the issue began?",
        ],
        "diagnostic_steps": [
            {
                "step": index + 1,
                "action": check,
                "why": "This check comes from the deterministic incident classifier.",
                "expected_signal": "A concrete signal that confirms or rules out this failure domain.",
            }
            for index, check in enumerate(checks)
        ],
        "escalation_criteria": [
            "Escalate when the issue persists after the deterministic checks.",
            "Include timestamps, minimal reproduction steps, error type/status, and request ID."
            + (f" Supplied request ID: {request_id}." if request_id else ""),
        ],
        "customer_response": (
            "Thanks for the details. We identified an initial failure domain and are working "
            "through focused checks to confirm the cause. We’ll use the request details you "
            "provided to narrow the issue and escalate with the relevant diagnostics if needed."
        ),
        "escalation_summary": (
            f"Deterministic fallback used because Claude analysis was unavailable or invalid: {reason}. "
            f"Initial failure domain: {classification['category']}."
        ),
        "_fallback": True,
        "_fallback_reason": reason,
    }


def analyze_incident(
    issue_title: str,
    status_code: str,
    endpoint: str,
    request_id: str,
    request_context: str,
    logs: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    safe_title = sanitize(issue_title)
    safe_endpoint = sanitize(endpoint)
    safe_request_id = sanitize(request_id)
    safe_context = sanitize(request_context)
    safe_logs = sanitize(logs)

    classification = classify_incident(status_code, safe_context, safe_logs).to_dict()

    metadata: dict[str, Any] = {
        "rule_based_classification": classification,
        "sanitization_applied": True,
        "fallback_used": False,
        "json_retry_used": False,
    }

    try:
        client = ClaudeSupportClient()

        prompt = build_prompt(
            issue_title=safe_title,
            status_code=status_code,
            endpoint=safe_endpoint,
            request_id=safe_request_id,
            request_context=safe_context,
            logs=safe_logs,
            classification=classification,
        )

        raw_output, claude_meta = client.analyze(prompt, max_tokens=5000)
        metadata.update(claude_meta)

        valid, parsed, error = validate_model_output(raw_output)

        # One compact retry protects the live demo from occasional malformed/truncated JSON.
        if not valid or parsed is None:
            metadata["json_retry_used"] = True
            metadata["first_validation_error"] = error

            retry_prompt = build_prompt(
                issue_title=safe_title,
                status_code=status_code,
                endpoint=safe_endpoint,
                request_id=safe_request_id,
                request_context=safe_context,
                logs=safe_logs,
                classification=classification,
                compact_retry=True,
            )

            retry_output, retry_meta = client.analyze(retry_prompt, max_tokens=5000)
            metadata["retry_claude_request_id"] = retry_meta.get("claude_request_id")
            metadata["retry_stop_reason"] = retry_meta.get("stop_reason")
            metadata["retry_output_tokens"] = retry_meta.get("output_tokens")

            valid, parsed, error = validate_model_output(retry_output)

        if not valid or parsed is None:
            metadata["fallback_used"] = True
            metadata["validation_error"] = error
            return _fallback_report(
                safe_title, safe_request_id, classification, error
            ), metadata

        return parsed, metadata

    except Exception as exc:
        reason = str(exc)
        metadata["fallback_used"] = True
        metadata["claude_error"] = reason
        return _fallback_report(
            safe_title, safe_request_id, classification, reason
        ), metadata
