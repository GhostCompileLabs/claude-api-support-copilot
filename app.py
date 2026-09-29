from __future__ import annotations
import os

import json
import tempfile
from pathlib import Path

import gradio as gr

from support_engine import analyze_incident


CSS = """
:root {
  --navy-950: #081120;
  --navy-900: #0d1b2a;
  --navy-800: #14263a;
  --navy-700: #1b3550;
  --blue-500: #4f8cff;
  --blue-400: #73a6ff;
  --cyan-400: #62d9ff;
  --green-400: #3ddc97;
  --amber-400: #f6c453;
  --red-400: #ff7b7b;
  --surface: #ffffff;
  --surface-soft: #f7f9fc;
  --text: #142033;
  --muted: #6e7b8f;
  --border: #e3e8ef;
}

html, body {
  background:
    radial-gradient(circle at 10% 0%, rgba(79, 140, 255, 0.10), transparent 28%),
    linear-gradient(180deg, #f5f8fc 0%, #eef3f8 100%) !important;
}

.gradio-container {
  max-width: 1380px !important;
  margin: 0 auto !important;
  padding: 20px 18px 42px !important;
  background: transparent !important;
}

/* ---------- HERO ---------- */
#app-hero {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 28px 30px;
  margin-bottom: 18px;
  background:
    radial-gradient(circle at 88% 18%, rgba(98, 217, 255, 0.20), transparent 24%),
    radial-gradient(circle at 70% 120%, rgba(79, 140, 255, 0.25), transparent 35%),
    linear-gradient(135deg, var(--navy-950) 0%, var(--navy-900) 55%, #143457 100%);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 18px 46px rgba(13, 27, 42, 0.20);
}

#app-hero h1 {
  color: #fff !important;
  margin: 0 0 8px !important;
  font-size: 2.15rem !important;
  letter-spacing: -0.03em;
}

#app-hero p {
  color: #d6e5f7 !important;
  margin: 0 !important;
  max-width: 820px;
  line-height: 1.55;
}

.hero-kicker {
  display: inline-block;
  font-size: 0.77rem;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #9fc5ff;
  margin-bottom: 10px;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 11px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  color: #f3f8ff;
  font-size: 0.84rem;
  font-weight: 650;
}

/* ---------- SECTION / CARDS ---------- */
.panel-card {
  border: 1px solid var(--border) !important;
  border-radius: 20px !important;
  background: rgba(255,255,255,0.96) !important;
  box-shadow: 0 10px 28px rgba(23, 42, 67, 0.07);
  padding: 6px 8px 10px;
}

.section-title {
  padding: 8px 8px 2px;
}

.section-title h3 {
  margin: 0 !important;
  font-size: 1rem !important;
  color: #17243a !important;
}

.section-title p {
  margin: 3px 0 0 !important;
  color: var(--muted) !important;
  font-size: 0.88rem !important;
}

/* ---------- INPUTS ---------- */
.gradio-container label,
.gradio-container .label-wrap {
  font-weight: 650 !important;
}

.gradio-container textarea,
.gradio-container input,
.gradio-container [role="combobox"] {
  border-radius: 12px !important;
}

.gradio-container textarea:focus,
.gradio-container input:focus,
.gradio-container [role="combobox"]:focus-within {
  box-shadow: 0 0 0 3px rgba(79, 140, 255, 0.13) !important;
}

#analyze-btn {
  min-height: 48px !important;
  border-radius: 13px !important;
  font-weight: 750 !important;
  font-size: 1rem !important;
  box-shadow: 0 8px 20px rgba(79, 140, 255, 0.18);
}

/* ---------- SECURITY NOTE ---------- */
.security-note {
  border-radius: 13px;
  border: 1px solid #dbe5f0;
  background: #f8fbff;
  padding: 11px 13px;
  color: #536176;
  font-size: 0.87rem;
}

/* ---------- RESULT SHELL ---------- */
#result-shell {
  min-height: 680px;
}

.result-placeholder {
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px dashed #d7e0eb;
  border-radius: 16px;
  background: linear-gradient(180deg, #fbfcfe 0%, #f6f9fc 100%);
  color: #7a8799;
  padding: 40px;
}

.result-placeholder .icon {
  font-size: 2.2rem;
  margin-bottom: 10px;
}

/* ---------- STATUS BAR ---------- */
#status-strip {
  margin: 0 0 10px;
}

.status-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  background: #ffffff;
  padding: 14px 16px;
}

.status-label {
  font-size: 0.73rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8a96a8;
  font-weight: 800;
  margin-bottom: 4px;
}

.status-value {
  font-size: 1.05rem;
  font-weight: 760;
  color: #1b2a40;
}

/* ---------- REPORT ---------- */
#report-output {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px 20px !important;
  background: #fff;
}

#report-output h1 {
  font-size: 1.55rem !important;
  margin-top: 0 !important;
  padding-bottom: 10px;
  border-bottom: 1px solid #edf1f5;
}

#report-output h3 {
  margin-top: 1.35rem !important;
  font-size: 1.03rem !important;
  color: #17243a !important;
}

#report-output blockquote {
  border-left: 4px solid var(--blue-500) !important;
  background: #f5f9ff !important;
  border-radius: 8px;
  padding: 10px 13px !important;
}

/* ---------- CUSTOMER REPLY ---------- */
#customer-card {
  border: 1px solid #dce8f8 !important;
  background: linear-gradient(180deg, #fafdff 0%, #f4f9ff 100%) !important;
}

/* ---------- ACCORDIONS / TABS ---------- */
.gradio-container .tab-nav {
  background: #fff !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 4px !important;
  margin-bottom: 14px !important;
}

.gradio-container .tab-nav button {
  border-radius: 10px !important;
  font-weight: 700 !important;
}

.gradio-container .tab-nav button.selected {
  background: #edf4ff !important;
  color: #2459aa !important;
}

.gradio-container .accordion {
  border-radius: 15px !important;
}

/* ---------- FOOTER ---------- */
.app-footer {
  text-align: center;
  color: #8290a3;
  font-size: 0.82rem;
  padding-top: 8px;
}

/* ---------- RESPONSIVE ---------- */
@media (max-width: 900px) {
  #app-hero {
    padding: 22px 20px;
    border-radius: 18px;
  }
  #app-hero h1 {
    font-size: 1.72rem !important;
  }
  .gradio-container {
    padding: 10px 10px 28px !important;
  }
}
"""


def _pretty(value: str) -> str:
    return str(value or "unknown").replace("_", " ").title()


def status_html(report: dict, metadata: dict) -> str:
    cls = report.get("classification", {})
    fallback = bool(report.get("_fallback"))
    mode = "Deterministic fallback" if fallback else "Live Claude"
    mode_icon = "🟠" if fallback else "🟢"

    return f"""
<div id="status-strip">
  <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;">
    <div class="status-card">
      <div class="status-label">Analysis mode</div>
      <div class="status-value">{mode_icon} {mode}</div>
    </div>
    <div class="status-card">
      <div class="status-label">Failure domain</div>
      <div class="status-value">{_pretty(cls.get("failure_domain"))}</div>
    </div>
    <div class="status-card">
      <div class="status-label">Severity</div>
      <div class="status-value">{_pretty(cls.get("severity"))}</div>
    </div>
    <div class="status-card">
      <div class="status-label">Retryable</div>
      <div class="status-value">{str(cls.get("retryable", "unknown"))}</div>
    </div>
  </div>
</div>
"""


def render_markdown(report: dict, metadata: dict) -> str:
    classification = report.get("classification", {})

    causes = "\n".join(
        (
            f"- **{item.get('cause', 'Unknown')}** "
            f"— confidence: **{item.get('confidence', 'unknown')}**  \n"
            f"  **Evidence:** {item.get('evidence', 'insufficient evidence')}  \n"
            f"  **Would weaken this hypothesis:** {item.get('disconfirming_signal', 'Not specified')}"
        )
        for item in report.get("likely_causes", [])
    ) or "- No likely causes returned."

    questions = "\n".join(
        f"- {q}" for q in report.get("clarification_questions", [])
    ) or "- None."

    steps = "\n".join(
        (
            f"{item.get('step', i + 1)}. **{item.get('action', '')}**  \n"
            f"   *Why:* {item.get('why', '')}  \n"
            f"   *Expected signal:* {item.get('expected_signal', '')}"
        )
        for i, item in enumerate(report.get("diagnostic_steps", []))
    ) or "No diagnostic steps returned."

    escalation = "\n".join(
        f"- {item}" for item in report.get("escalation_criteria", [])
    ) or "- None."

    evidence = "\n".join(
        f"- {item}" for item in report.get("evidence_used", [])
    ) or "- No evidence listed."

    return f"""
# Incident Analysis

### Executive summary
{report.get("issue_summary", "")}

### Evidence used
{evidence}

### Likely causes
{causes}

### Clarification questions
{questions}

### Diagnostic plan
{steps}

### Escalation criteria
{escalation}

### Internal escalation summary
{report.get("escalation_summary", "")}
""".strip()


def _make_report_file(report_md: str, customer_reply: str, metadata: dict) -> str:
    report_dir = Path(tempfile.gettempdir()) / "claude_support_copilot_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "incident-report.md"
    path.write_text(
        report_md
        + "\n\n---\n\n## Customer-ready response\n\n"
        + customer_reply
        + "\n\n---\n\n## Internal metadata\n\n```json\n"
        + json.dumps(metadata, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    return str(path)


def run_analysis(
    issue_title: str,
    status_code: str,
    endpoint: str,
    request_id: str,
    request_context: str,
    logs: str,
):
    if not issue_title.strip() and not request_context.strip() and not logs.strip():
        raise gr.Error("Add an issue title, request context, or sanitized logs.")

    report, metadata = analyze_incident(
        issue_title=issue_title,
        status_code=status_code,
        endpoint=endpoint,
        request_id=request_id,
        request_context=request_context,
        logs=logs,
    )

    report_md = render_markdown(report, metadata)
    customer_reply = report.get("customer_response", "")
    report_file = _make_report_file(report_md, customer_reply, metadata)

    return (
        status_html(report, metadata),
        report_md,
        customer_reply,
        metadata,
        report_file,
    )


with gr.Blocks(title="Claude API Support Copilot") as demo:
    gr.HTML(
        """
        <div id="app-hero">
          <div class="hero-kicker">Enterprise Support Engineering</div>
          <h1>Claude API Support Copilot</h1>
          <p>
            Triage Claude API incidents with deterministic classification, evidence-grounded
            analysis, customer-ready communication, and request-ID-aware escalation.
          </p>
          <div class="hero-badges">
            <span class="hero-badge">◆ Live Claude API</span>
            <span class="hero-badge">✓ Secret Redaction</span>
            <span class="hero-badge">◎ Evidence Grounding</span>
            <span class="hero-badge">↗ Escalation Ready</span>
            <span class="hero-badge">↺ Graceful Fallback</span>
          </div>
        </div>
        """
    )

    with gr.Tabs():
        with gr.Tab("Incident Console"):
            with gr.Row(equal_height=False):
                with gr.Column(scale=5, elem_classes=["panel-card"]):
                    gr.HTML(
                        """
                        <div class="section-title">
                          <h3>Incident details</h3>
                          <p>Paste sanitized technical context. Keep secrets and customer-sensitive data out.</p>
                        </div>
                        """
                    )

                    issue_title = gr.Textbox(
                        label="Issue title",
                        placeholder="Production requests returning intermittent 429 errors",
                    )

                    with gr.Row():
                        status_code = gr.Dropdown(
                            ["", "400", "401", "403", "404", "413", "429", "500", "504", "529"],
                            value="",
                            label="HTTP status",
                        )
                        endpoint = gr.Textbox(
                            label="Endpoint / operation",
                            placeholder="/v1/messages",
                        )

                    request_id = gr.Textbox(
                        label="Request ID",
                        placeholder="req_...  (optional but useful for escalation)",
                    )

                    request_context = gr.Textbox(
                        label="Sanitized request context",
                        lines=7,
                        placeholder=(
                            "What changed? Is the issue intermittent? Approximate traffic/concurrency? "
                            "What succeeds or fails?"
                        ),
                    )

                    logs = gr.Textbox(
                        label="Sanitized error / logs",
                        lines=7,
                        placeholder='{"type":"error","error":{"type":"rate_limit_error","message":"..."}}',
                    )

                    analyze_btn = gr.Button(
                        "Analyze incident",
                        variant="primary",
                        elem_id="analyze-btn",
                    )

                    gr.HTML(
                        """
                        <div class="security-note">
                          🔒 <b>Security:</b> Never paste API keys, bearer tokens, passwords,
                          personal data, or customer-sensitive content.
                        </div>
                        """
                    )

                with gr.Column(scale=7, elem_classes=["panel-card"], elem_id="result-shell"):
                    gr.HTML(
                        """
                        <div class="section-title">
                          <h3>Support analysis</h3>
                          <p>Evidence, hypotheses, diagnostics, customer response, and escalation handoff.</p>
                        </div>
                        """
                    )

                    status_output = gr.HTML(
                        """
                        <div class="result-placeholder">
                          <div>
                            <div class="icon">🛠️</div>
                            <b>Ready to analyze</b><br>
                            Enter an incident on the left and select <b>Analyze incident</b>.
                          </div>
                        </div>
                        """
                    )

                    report_output = gr.Markdown(
                        visible=False,
                        elem_id="report-output",
                    )

                    customer_reply = gr.Textbox(
                        label="Customer-ready reply",
                        lines=7,
                        interactive=False,
                        visible=False,
                        elem_id="customer-card",
                    )

                    report_download = gr.File(
                        label="Download incident report",
                        visible=False,
                    )

            with gr.Accordion("Engineering metadata", open=False):
                metadata_output = gr.JSON(label="Internal metadata")

            gr.HTML(
                """
                <div class="section-title" style="margin-top:8px;">
                  <h3>Quick test scenarios</h3>
                  <p>Load a scenario, then run the analysis.</p>
                </div>
                """
            )

            gr.Examples(
                examples=[
                    [
                        "Production requests returning intermittent 429 errors",
                        "429",
                        "/v1/messages",
                        "req_example_rate_001",
                        "Traffic increased after a batch job started. Around 40 concurrent requests are being sent. Failed requests usually succeed after waiting several seconds and retrying.",
                        '{"type":"error","error":{"type":"rate_limit_error","message":"Rate limit reached. Please retry after a short delay."}}',
                    ],
                    [
                        "Requests fail after credential rotation",
                        "401",
                        "/v1/messages",
                        "req_example_auth_002",
                        "Requests worked before a credential rotation. Immediately after deployment, all new requests began failing. No other application change was made.",
                        '{"type":"error","error":{"type":"authentication_error","message":"Invalid API key"}}',
                    ],
                    [
                        "Intermittent overloaded responses",
                        "529",
                        "/v1/messages",
                        "req_example_overload_003",
                        "The same request sometimes succeeds and sometimes fails during high traffic. Retrying after a short delay usually succeeds.",
                        '{"type":"error","error":{"type":"overloaded_error","message":"The API is temporarily overloaded"}}',
                    ],
                ],
                inputs=[
                    issue_title,
                    status_code,
                    endpoint,
                    request_id,
                    request_context,
                    logs,
                ],
            )

            analyze_btn.click(
                fn=run_analysis,
                inputs=[
                    issue_title,
                    status_code,
                    endpoint,
                    request_id,
                    request_context,
                    logs,
                ],
                outputs=[
                    status_output,
                    report_output,
                    customer_reply,
                    metadata_output,
                    report_download,
                ],
            ).then(
                fn=lambda: (
                    gr.update(visible=True),
                    gr.update(visible=True),
                    gr.update(visible=True),
                ),
                outputs=[report_output, customer_reply, report_download],
            )

        with gr.Tab("Architecture"):
            with gr.Row():
                with gr.Column(scale=7, elem_classes=["panel-card"]):
                    gr.Markdown(
                        """
## Request flow

```text
Sanitized incident
      ↓
Secret redaction
      ↓
Deterministic classifier
      ↓
Claude API analysis
      ↓
Schema validation
      ↓
Valid report ───────────────┐
      │                      │
      └─ API/model failure ──┤
                             ↓
                    Deterministic fallback
                             ↓
             Customer reply + escalation handoff
```
"""
                    )

                with gr.Column(scale=5, elem_classes=["panel-card"]):
                    gr.Markdown(
                        """
## Reliability controls

**Deterministic first**  
Known error domains are classified before the model runs.

**Grounded analysis**  
Likely causes must point back to supplied evidence.

**Graceful degradation**  
Support guidance remains available if Claude is unavailable.

**Request-ID aware**  
Escalation artifacts preserve request identifiers.

**Secret redaction**  
Common credential patterns are removed before model calls.
"""
                    )

    gr.HTML(
        """
        <div class="app-footer">
          Claude API Support Copilot · Python · Gradio · Anthropic SDK
        </div>
        """
    )


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
        ),
        css=CSS,
        footer_links=["gradio"],
    )
