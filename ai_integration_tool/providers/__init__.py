"""AI provider implementations (OpenRouter, YandexGPT, etc.)."""
from __future__ import annotations

from .base import BaseProvider, ChatMessage, ProviderError
from .openrouter import OpenRouterProvider
from .yandex_gpt import YandexGPTProvider

PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "openrouter": OpenRouterProvider,
    "yandex_gpt": YandexGPTProvider,
}


def get_provider(name: str, config: dict) -> BaseProvider:
    """Instantiate a provider by name using global config."""
    if name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDER_REGISTRY)}")
    return PROVIDER_REGISTRY[name](config)
