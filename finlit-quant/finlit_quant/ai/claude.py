"""Claude as the analyst, streamed through the official Anthropic SDK."""

from __future__ import annotations

from collections.abc import Iterator

import anthropic

from finlit_quant.ai import AIError

# Server-side refusal fallbacks are available on these models through the
# Claude API. "default" lets Anthropic route a declined request to the right
# substitute model by refusal category, so no model list is maintained here.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ClaudeProvider:
    def __init__(self, api_key: str, model: str, effort: str = "high") -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.effort = effort if effort in ("low", "medium", "high", "xhigh", "max") else "high"
        self.label = f"Claude ({model})"
        self.served_model: str | None = None

    def stream(self, system: str, messages: list[dict]) -> Iterator[str]:
        params = dict(
            model=self.model,
            max_tokens=64000,
            system=system,
            messages=messages,
            # Thinking is adaptive by default on current models; effort is
            # the dial. A research memo is worth "high".
            output_config={"effort": self.effort},
        )
        try:
            if self.model in FALLBACK_MODELS:
                ctx = self.client.beta.messages.stream(betas=[FALLBACK_BETA], fallbacks="default", **params)
            else:
                ctx = self.client.messages.stream(**params)
            with ctx as stream:
                for text in stream.text_stream:
                    yield text
                final = stream.get_final_message()
        except anthropic.AuthenticationError:
            raise AIError("Anthropic rejected the API key. Open Settings and paste a valid key from console.anthropic.com.") from None
        except anthropic.PermissionDeniedError:
            raise AIError(f"This Anthropic key does not have access to {self.model}. Pick another model in Settings.") from None
        except anthropic.NotFoundError:
            raise AIError(f"Anthropic does not recognise the model {self.model}. Pick another model in Settings.") from None
        except anthropic.RateLimitError:
            raise AIError("Anthropic is rate limiting this key. Wait a minute and try again.") from None
        except anthropic.BadRequestError as exc:
            raise AIError(f"Anthropic rejected the request: {exc.message}") from None
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                raise AIError("Anthropic's servers had a problem. Try again in a minute.") from None
            raise AIError(f"Anthropic returned an error ({exc.status_code}): {exc.message}") from None
        except anthropic.APIConnectionError:
            raise AIError("Could not reach Anthropic. Check your internet connection and try again.") from None

        self.served_model = getattr(final, "model", None) or self.model
        if final.stop_reason == "refusal":
            yield "\n\n*The model declined to continue this answer. Try rephrasing the question.*"
        elif final.stop_reason == "max_tokens":
            yield "\n\n*Stopped at the length limit.*"
