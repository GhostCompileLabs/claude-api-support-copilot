from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"(?i)(x-api-key\s*[:=]\s*)[A-Za-z0-9_\-]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(api[_ -]?key\s*[:=]\s*)[A-Za-z0-9_\-]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._\-]+"), r"\1[REDACTED]"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]+"), "[REDACTED_API_KEY]"),
]


def sanitize(text: str) -> str:
    value = text or ""
    for pattern, replacement in _PATTERNS:
        value = pattern.sub(replacement, value)
    return value
