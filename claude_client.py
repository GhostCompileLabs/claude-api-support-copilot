from __future__ import annotations

import os
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeSupportClient:
    def __init__(self) -> None:
        api_key = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is missing. Add it to .env locally or to your host's secret settings."
            )

        self.model = (os.getenv("CLAUDE_MODEL") or "claude-sonnet-5").strip()
        self.client = anthropic.Anthropic(api_key=api_key, max_retries=2)

    def analyze(self, prompt: str, max_tokens: int = 5000) -> tuple[str, dict[str, Any]]:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,
                system=(
                    "You are a precise enterprise technical support assistant. "
                    "Ground claims in supplied evidence, separate observations from hypotheses, "
                    "avoid overclaiming root cause, and obey the requested JSON schema exactly."
                ),
                messages=[{"role": "user", "content": prompt}],
            )

            text_blocks = [
                block.text
                for block in message.content
                if getattr(block, "type", None) == "text"
            ]
            text = "\n".join(text_blocks).strip()

            usage = getattr(message, "usage", None)
            meta = {
                "provider": "Anthropic",
                "model": self.model,
                "claude_request_id": getattr(message, "_request_id", None),
                "stop_reason": getattr(message, "stop_reason", None),
                "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
                "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
            }
            return text, meta

        except anthropic.AuthenticationError as exc:
            raise RuntimeError("Claude API authentication failed. Check the API key.") from exc
        except anthropic.PermissionDeniedError as exc:
            raise RuntimeError("Claude API permission denied for this credential/request.") from exc
        except anthropic.NotFoundError as exc:
            raise RuntimeError(
                f"Claude API resource/model not found. Check CLAUDE_MODEL={self.model}."
            ) from exc
        except anthropic.RateLimitError as exc:
            retry_after = None
            if getattr(exc, "response", None) is not None:
                retry_after = exc.response.headers.get("retry-after")
            suffix = f" Retry after {retry_after}s." if retry_after else ""
            raise RuntimeError(f"Claude API rate limit reached.{suffix}") from exc
        except anthropic.APIConnectionError as exc:
            raise RuntimeError("Could not connect to the Claude API.") from exc
        except anthropic.APIStatusError as exc:
            request_id = getattr(exc, "request_id", None)
            suffix = f" Request ID: {request_id}" if request_id else ""
            body = ""
            try:
                body = f" {exc.response.text[:300]}"
            except Exception:
                pass
            raise RuntimeError(
                f"Claude API returned HTTP {exc.status_code}.{suffix}{body}"
            ) from exc
