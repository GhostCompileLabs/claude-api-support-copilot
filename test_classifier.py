from classifier import classify_incident
from sanitizer import sanitize


def test_rate_limit():
    result = classify_incident("429", "", "rate_limit_error")
    assert result.category == "rate_limit"
    assert result.retryable is True


def test_auth():
    result = classify_incident("401", "", "authentication_error")
    assert result.category == "authentication"
    assert result.retryable is False


def test_sanitizer():
    cleaned = sanitize("x-api-key: sk-ant-secret123")
    assert "secret123" not in cleaned
    assert "REDACTED" in cleaned
