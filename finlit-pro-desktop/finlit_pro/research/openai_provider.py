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
        except openai.BadRequestError as exc:
            # First Version: a 400 fell through to "OpenAI returned an error (400)" and the cause was dropped.
            raise AnalysisError(f"OpenAI rejected the request: {exc.message}") from None
        except openai.APIStatusError as exc:
            raise AnalysisError(f"OpenAI returned an error ({exc.status_code}).") from None
        except openai.APIConnectionError:
            raise AnalysisError("Could not reach OpenAI. Check the internet connection.") from None
        # First Version: this call cannot be interrupted, and a note that finished after Cancel was shown anyway.
        # Current Version: a cancelled run discards the answer.
        if cancelled and cancelled():
            raise AnalysisError("Analysis cancelled.")
        choice = resp.choices[0] if resp.choices else None
        if choice is not None and getattr(choice, "finish_reason", None) == "length":
            # First Version: a cut-off answer was reported as "no analysis" or as invalid JSON.
            raise AnalysisError(
                "The analysis exceeded the output limit (the model's reasoning counts toward it). "
                "Reduce the filing excerpt length in Settings or choose another model, then run it again."
            )
        message = choice.message if choice is not None else None
        if message is not None and getattr(message, "refusal", None):
            raise AnalysisError("The model declined to produce this analysis.")
        text = (message.content if message is not None else "") or ""
        if not text:
            raise AnalysisError("The model returned no analysis.")
        if progress:
            progress(len(text))
        return text


def check_access(api_key: str, model: str) -> str:
    """Confirm the key works and can see `model` (or the fallback), through the free Models API."""
    client = openai.OpenAI(api_key=api_key, max_retries=1, timeout=20)
    try:
        for candidate in (model, FALLBACK_MODEL):
            try:
                found = client.models.retrieve(candidate)
            except openai.NotFoundError:
                continue
            if candidate == model:
                return f"Key works. {found.id} is available."
            return f"Key works, but {model} is not available to it; the note will use {found.id}."
    except openai.AuthenticationError:
        raise AnalysisError("OpenAI rejected this key. Check it was copied in full (it starts with sk-).") from None
    except openai.PermissionDeniedError:
        raise AnalysisError(f"The key works but cannot use {model}.") from None
    except openai.RateLimitError:
        raise AnalysisError("The key works but is rate limited or out of credit.") from None
    except openai.APIStatusError as exc:
        raise AnalysisError(f"OpenAI returned an error ({exc.status_code}).") from None
    except openai.APIConnectionError:
        raise AnalysisError("Could not reach OpenAI. Check the internet connection.") from None
    raise AnalysisError(f"The key works, but neither {model} nor {FALLBACK_MODEL} is available to it. Choose another model.")
