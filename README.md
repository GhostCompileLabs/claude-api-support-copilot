---
title: Claude API Support Copilot
emoji: 🛠️
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 6.28.0
app_file: app.py
pinned: false
---

# Claude API Support Copilot

A portfolio project for enterprise Claude API support workflows, built with **Python, Gradio, and the Anthropic SDK**.

## What the app demonstrates

- deterministic API incident classification
- common 400 / 401 / 403 / 413 / 429 / 5xx / 529 / timeout handling
- input secret redaction
- live Claude API analysis
- evidence-grounded root-cause hypotheses
- confidence calibration
- JSON/schema validation
- one compact retry for malformed or truncated model output
- graceful deterministic fallback
- request-ID-aware escalation
- customer-ready support communication
- downloadable incident reports

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Put your API key in `.env`:

```env
ANTHROPIC_API_KEY=your_real_key
CLAUDE_MODEL=claude-sonnet-5
```

Then:

```bash
python app.py
```

Open the local Gradio URL.

## Hugging Face Spaces deployment

1. Create a new **Gradio** Space.
2. Upload all project files **except `.env` and `.venv`**.
3. In **Space Settings → Variables and secrets**, add:
   - Secret: `ANTHROPIC_API_KEY`
   - Variable (optional): `CLAUDE_MODEL=claude-sonnet-5`
4. Let the Space rebuild.
5. Test a 429 incident and confirm `fallback_used` is `false`.

Never commit or upload `.env`.

## Suggested validation scenarios

### 429 rate limit
- Increased burst traffic
- Retry succeeds after delay
- Expect rate-limit classification and pacing/backoff diagnostics

### 401 authentication
- Issue starts immediately after credential rotation
- Expect credential/configuration checks

### 403 permission
- Authentication succeeds, selected resource fails
- Expect authorization/workspace/model access checks

### 529 overload
- Intermittent failures recover on retry
- Expect transient overload/backoff guidance

## Resume-ready description

**Claude API Support Copilot | Python, Gradio, Claude API**

Built an enterprise API support copilot that combines deterministic incident classification
with evidence-grounded Claude analysis. Implemented secret redaction, confidence-calibrated
diagnostics, structured-response validation, request-ID tracking, customer-ready response
generation, and graceful fallback during API/model failures.
