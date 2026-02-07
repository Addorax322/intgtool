"""Abstract base for AI providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Iterator


@dataclass
class ChatMessage:
    """Single message in a chat."""
    role: str  # "system", "user", "assistant"
    content: str


class ProviderError(Exception):
    """Raised when a provider API call fails (after retries)."""
    pass


class BaseProvider(ABC):
    """Interface that all AI providers must implement."""

    def __init__(self, config: dict):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'openrouter')."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """
        Send messages and return full text or an iterator of chunks if stream=True.
        """
        pass

    def supports_streaming(self, model: str) -> bool:
        """Override in subclass if only some models support streaming."""
        return True
