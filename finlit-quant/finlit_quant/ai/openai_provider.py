"""OpenAI as the analyst, for anyone who already has a key from the FinLit Pro website."""

from __future__ import annotations

from collections.abc import Iterator

import openai

from finlit_quant.ai import AIError

# Same fallback the website's advisor uses when a key lacks the primary model.
FALLBACK_MODEL = "gpt-5.4-nano"


class OpenAIProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.label = f"OpenAI ({model})"
        self.served_model: str | None = None

    def _open(self, model: str, system: str, messages: list[dict]):
        return self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, *messages],
            stream=True,
            max_completion_tokens=8000,
        )

    def stream(self, system: str, messages: list[dict]) -> Iterator[str]:
        try:
            try:
                chunks = self._open(self.model, system, messages)
                self.served_model = self.model
            except (openai.NotFoundError, openai.PermissionDeniedError):
                if self.model == FALLBACK_MODEL:
                    raise
                chunks = self._open(FALLBACK_MODEL, system, messages)
                self.served_model = FALLBACK_MODEL
            for chunk in chunks:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except openai.AuthenticationError:
            raise AIError("OpenAI rejected the API key. Open Settings and paste a valid key.") from None
        except (openai.NotFoundError, openai.PermissionDeniedError):
            raise AIError(f"This OpenAI key cannot use {self.model} or {FALLBACK_MODEL}. Pick another model in Settings.") from None
        except openai.RateLimitError:
            raise AIError("OpenAI is rate limiting this key, or it is out of credit. Wait a minute or check billing.") from None
        except openai.APIStatusError as exc:
            raise AIError(f"OpenAI returned an error ({exc.status_code}). Try again in a minute.") from None
        except openai.APIConnectionError:
            raise AIError("Could not reach OpenAI. Check your internet connection and try again.") from None
