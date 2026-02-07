"""AI provider implementations (OpenRouter, etc.)."""
from __future__ import annotations

from .base import BaseProvider, ChatMessage, ProviderError
from .openrouter import OpenRouterProvider

PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "openrouter": OpenRouterProvider,
}


def get_provider(name: str, config: dict) -> BaseProvider:
    """Instantiate a provider by name using global config."""
    if name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDER_REGISTRY)}")
    return PROVIDER_REGISTRY[name](config)
