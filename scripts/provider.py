"""Provider abstraction for The Stephanie Project.

Phase 1 defaults to a deterministic stub provider.
Real providers (OpenAI, Anthropic, etc.) should implement the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str
    params: dict[str, Any]


@dataclass(frozen=True)
class ProviderResult:
    text: str
    provider_name: str
    model: str
    request_id: str | None = None
    usage: dict[str, Any] | None = None


class Provider(Protocol):
    def generate(
        self,
        *,
        agent_name: str,
        system_prompt: str,
        user_payload: str,
        config: ProviderConfig,
    ) -> ProviderResult: ...


class StubProvider:
    """Deterministic provider used until a real client is wired."""

    def __init__(self, stub_fn: Callable[[str, str], str]):
        self._stub_fn = stub_fn

    def generate(
        self,
        *,
        agent_name: str,
        system_prompt: str,
        user_payload: str,
        config: ProviderConfig,
    ) -> ProviderResult:
        # Intentionally ignores prompt; stub_fn must be deterministic.
        text = self._stub_fn(agent_name, user_payload)
        return ProviderResult(text=text, provider_name=config.name, model=config.model)


def resolve_provider_config(
    raw_provider: dict[str, Any] | None,
    *,
    model_override: str | None = None,
) -> ProviderConfig:
    raw_provider = raw_provider or {}
    name = str(raw_provider.get("name") or "stub")
    model = str(model_override or raw_provider.get("model") or "stub-model")

    params: dict[str, Any] = {}
    for key in (
        "api_key_env",
        "base_url",
        "temperature",
        "top_p",
        "max_output_tokens",
        "seed",
        "timeout_seconds",
        "max_retries",
    ):
        if key in raw_provider and raw_provider[key] is not None:
            params[key] = raw_provider[key]

    return ProviderConfig(name=name, model=model, params=params)
