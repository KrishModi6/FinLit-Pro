"""API keys in the operating system's credential store.

Windows: Credential Manager. macOS: Keychain. Linux: Secret Service.
An environment variable, when set, takes precedence and nothing is stored.
If no secure store is available the key is not saved at all, rather than
falling back to a plain-text file.
"""

from __future__ import annotations

import os

SERVICE = "FinLitPro"
ENV_VARS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


class CredentialError(RuntimeError):
    """The secure store refused or is unavailable; the message says what to do."""


def _keyring():
    try:
        import keyring
        from keyring.errors import KeyringError
    except ImportError:  # pragma: no cover - keyring is a hard dependency
        return None, Exception
    return keyring, KeyringError


def get(name: str) -> str:
    env = os.environ.get(ENV_VARS.get(name, ""), "").strip()
    if env:
        return env
    keyring, err = _keyring()
    if keyring is None:
        return ""
    try:
        return (keyring.get_password(SERVICE, name) or "").strip()
    except err:
        return ""


def source(name: str) -> str:
    """Where the key comes from, for display: never the key itself."""
    if os.environ.get(ENV_VARS.get(name, ""), "").strip():
        return f"environment variable {ENV_VARS[name]}"
    return "credential store" if get(name) else "not set"


def store(name: str, value: str) -> None:
    keyring, err = _keyring()
    if keyring is None:
        raise CredentialError("The keyring package is missing. Reinstall the requirements.")
    try:
        if value:
            keyring.set_password(SERVICE, name, value)
        else:
            try:
                keyring.delete_password(SERVICE, name)
            except err:
                pass  # nothing stored
    except err as exc:
        raise CredentialError(
            f"No secure credential store is available on this system ({exc.__class__.__name__}). "
            f"Set the {ENV_VARS.get(name, name)} environment variable instead."
        ) from None


def backend() -> str:
    keyring, _ = _keyring()
    if keyring is None:
        return "unavailable"
    return type(keyring.get_keyring()).__name__
