"""Claude as the analysis engine, through the official Anthropic SDK.

The note is requested as structured output (`output_config.format` with a
JSON schema), so the response is guaranteed to parse into facts,
interpretation, risks and uncertainties. It is streamed so long notes do
not hit HTTP timeouts, and server-side refusal fallbacks are on for the
models that support them.
"""

from __future__ import annotations

from collections.abc import Callable

import anthropic

from finlit_pro.research import AnalysisError
from finlit_pro.research.note import SCHEMA

FALLBACK_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ClaudeEngine:
    def __init__(self, api_key: str, model: str, effort: str = "high") -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.effort = effort if effort in ("low", "medium", "high", "xhigh", "max") else "high"
        self.label = f"Claude {model}"
        self.served_model: str | None = None

    def run(self, system: str, user: str, progress: Callable[[int], None] | None = None, cancelled: Callable[[], bool] | None = None) -> str:
        params = dict(
            model=self.model,
            max_tokens=32000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": SCHEMA}},
        )
        received = 0
        try:
            if self.model in FALLBACK_MODELS:
                ctx = self.client.beta.messages.stream(betas=[FALLBACK_BETA], fallbacks="default", **params)
            else:
                ctx = self.client.messages.stream(**params)
            with ctx as stream:
                for text in stream.text_stream:
                    received += len(text)
                    if progress:
                        progress(received)
                    if cancelled and cancelled():
                        raise AnalysisError("Analysis cancelled.")
                final = stream.get_final_message()
        except anthropic.AuthenticationError:
            raise AnalysisError("Anthropic rejected the API key. Update it in Settings > Analysis.") from None
        except anthropic.PermissionDeniedError:
            raise AnalysisError(f"This Anthropic key cannot use {self.model}. Choose another model in Settings.") from None
        except anthropic.NotFoundError:
            raise AnalysisError(f"Anthropic does not recognise the model {self.model}.") from None
        except anthropic.RateLimitError:
            raise AnalysisError("Anthropic is rate limiting this key. Try again in a minute.") from None
        except anthropic.BadRequestError as exc:
            raise AnalysisError(f"Anthropic rejected the request: {exc.message}") from None
        except anthropic.APIStatusError as exc:
            raise AnalysisError(f"Anthropic returned an error ({exc.status_code}). Try again shortly.") from None
        except anthropic.APIConnectionError:
            raise AnalysisError("Could not reach Anthropic. Check the internet connection.") from None

        self.served_model = getattr(final, "model", None) or self.model
        if final.stop_reason == "refusal":
            raise AnalysisError("The model declined to produce this analysis.")
        if final.stop_reason == "max_tokens":
            raise AnalysisError("The analysis exceeded the output limit. Reduce the filing excerpt length in Settings and run it again.")
        text = next((b.text for b in final.content if getattr(b, "type", "") == "text"), "")
        if not text:
            raise AnalysisError("The model returned no analysis.")
        return text
