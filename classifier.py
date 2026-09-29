from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Classification:
    category: str
    severity: str
    retryable: bool
    evidence: list[str]
    recommended_checks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_incident(status_code: str, request_context: str, logs: str) -> Classification:
    text = f"{status_code} {request_context} {logs}".lower()
    code = str(status_code or "").strip()

    rules = [
        (
            code == "401" or "authentication_error" in text or "invalid api key" in text,
            Classification(
                "authentication", "high", False,
                ["HTTP 401 / authentication-related evidence detected."],
                [
                    "Confirm the credential is present, current, and loaded by the running process.",
                    "Confirm the credential belongs to the intended organization/workspace.",
                    "Reproduce with a minimal request after credential validation.",
                ],
            ),
        ),
        (
            code == "403" or "permission_error" in text or "forbidden" in text,
            Classification(
                "permission", "high", False,
                ["HTTP 403 / permission-related evidence detected."],
                [
                    "Verify access to the requested model/resource.",
                    "Confirm organization/workspace permissions.",
                    "Reproduce with a known-good credential and minimal request.",
                ],
            ),
        ),
        (
            code == "429" or "rate_limit_error" in text or "rate limit" in text,
            Classification(
                "rate_limit", "medium", True,
                ["HTTP 429 / rate-limit evidence detected."],
                [
                    "Capture retry-after and rate-limit response headers when available.",
                    "Compare request pacing and token volume with the applicable limits.",
                    "Use exponential backoff with jitter and smooth burst traffic.",
                ],
            ),
        ),
        (
            code == "529" or "overloaded_error" in text or "overloaded" in text,
            Classification(
                "overloaded", "medium", True,
                ["HTTP 529 / overload evidence detected."],
                [
                    "Retry with exponential backoff and jitter.",
                    "Check whether failures are transient or sustained.",
                    "Capture timestamps and request IDs for persistent failures.",
                ],
            ),
        ),
        (
            code == "413" or "request_too_large" in text or "too large" in text,
            Classification(
                "request_too_large", "medium", False,
                ["HTTP 413 / request-size evidence detected."],
                [
                    "Measure and reduce request payload size.",
                    "Remove unnecessary context or attachments.",
                    "Reproduce with a minimal payload.",
                ],
            ),
        ),
        (
            code == "400" or "invalid_request_error" in text or "bad request" in text,
            Classification(
                "invalid_request", "medium", False,
                ["HTTP 400 / invalid-request evidence detected."],
                [
                    "Validate request body and required fields.",
                    "Check model name and parameter compatibility.",
                    "Reproduce with the smallest valid request.",
                ],
            ),
        ),
        (
            code == "504" or "timeout_error" in text or "timeout" in text or "timed out" in text,
            Classification(
                "timeout", "medium", True,
                ["Timeout-related evidence detected."],
                [
                    "Determine whether the timeout is client-side, network-side, or upstream.",
                    "Capture request duration and timestamps.",
                    "Consider streaming or a smaller request for long-running responses.",
                ],
            ),
        ),
        (
            code.startswith("5") or "api_error" in text or "internal server error" in text,
            Classification(
                "server_error", "high", True,
                ["5xx / server-side error evidence detected."],
                [
                    "Retry with exponential backoff and jitter.",
                    "Capture request ID and timestamp.",
                    "Escalate if failures persist across independent requests.",
                ],
            ),
        ),
        (
            "connection" in text or "dns" in text or "network" in text or "tls" in text,
            Classification(
                "network", "high", True,
                ["Network/connection evidence detected."],
                [
                    "Validate DNS, proxy, firewall, and TLS connectivity.",
                    "Reproduce from another network path where possible.",
                    "Separate local connection failures from API HTTP responses.",
                ],
            ),
        ),
    ]

    for matched, result in rules:
        if matched:
            return result

    return Classification(
        "unknown", "medium", False,
        ["No deterministic rule matched the supplied evidence."],
        [
            "Collect the exact HTTP status and API error type.",
            "Capture request ID, timestamp, and minimal reproduction.",
            "Identify the most recent application/configuration change.",
        ],
    )
