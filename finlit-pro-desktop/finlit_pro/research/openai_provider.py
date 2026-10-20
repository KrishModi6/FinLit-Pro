"""OpenAI as the analysis engine, with the same JSON schema enforced."""

from __future__ import annotations

from collections.abc import Callable

import openai

from finlit_pro.research import AnalysisError
from finlit_pro.research.note import SCHEMA

FALLBACK_MODEL = "gpt-5.4-nano"


class OpenAIEngine:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.label = f"OpenAI {model}"
        self.served_model: str | None = None

    def _call(self, model: str, system: str, user: str):
        return self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_schema", "json_schema": {"name": "research_note", "strict": True, "schema": SCHEMA}},
            max_completion_tokens=16000,
        )

    def run(self, system: str, user: str, progress: Callable[[int], None] | None = None, cancelled: Callable[[], bool] | None = None) -> str:
        try:
            try:
                resp = self._call(self.model, system, user)
                self.served_model = self.model
            except (openai.NotFoundError, openai.PermissionDeniedError):
                if self.model == FALLBACK_MODEL:
                    raise
                resp = self._call(FALLBACK_MODEL, system, user)
                self.served_model = FALLBACK_MODEL
        except openai.AuthenticationError:
            raise AnalysisError("OpenAI rejected the API key. Update it in Settings > Analysis.") from None
        except (openai.NotFoundError, openai.PermissionDeniedError):
            raise AnalysisError(f"This OpenAI key cannot use {self.model} or {FALLBACK_MODEL}.") from None
        except openai.RateLimitError:
            raise AnalysisError("OpenAI is rate limiting this key or it is out of credit.") from None
        except openai.APIStatusError as exc:
            raise AnalysisError(f"OpenAI returned an error ({exc.status_code}).") from None
        except openai.APIConnectionError:
            raise AnalysisError("Could not reach OpenAI. Check the internet connection.") from None
        message = resp.choices[0].message if resp.choices else None
        if message is not None and getattr(message, "refusal", None):
            raise AnalysisError("The model declined to produce this analysis.")
        text = (message.content if message is not None else "") or ""
        if not text:
            raise AnalysisError("The model returned no analysis.")
        if progress:
            progress(len(text))
        return text
