"""OpenRouter API provider (DeepSeek, Qwen, Mistral, etc.)."""
from __future__ import annotations

import json
from typing import Iterator

import requests

from .base import BaseProvider, ChatMessage, ProviderError


class OpenRouterProvider(BaseProvider):
    """OpenRouter chat completions with optional streaming."""

    name = "openrouter"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://openrouter.ai/api/v1").rstrip("/")
        self.api_key = config.get("api_key", "")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _payload(self, messages: list[ChatMessage], model: str, max_tokens: int, stream: bool) -> dict:
        return {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "stream": stream,
        }

    def supports_streaming(self, model: str) -> bool:
        models_cfg = self.config.get("models", [])
        for m in models_cfg:
            if isinstance(m, dict) and m.get("id") == model:
                return m.get("supports_streaming", True)
        return True

    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> str | Iterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload = self._payload(messages, model, max_tokens, stream)
        if stream:
            return self._stream(url, payload)
        return self._complete(url, payload)

    def _complete(self, url: str, payload: dict) -> str:
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=120)
        if resp.status_code != 200:
            raise ProviderError(f"OpenRouter API error {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        return (choice.get("message") or {}).get("content", "")

    def _stream(self, url: str, payload: dict) -> Iterator[str]:
        with requests.post(
            url, headers=self._headers(), json=payload, stream=True, timeout=120
        ) as resp:
            if resp.status_code != 200:
                raise ProviderError(f"OpenRouter API error {resp.status_code}: {resp.text[:500]}")
            for line in resp.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8").strip()
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        obj = json.loads(data_str)
                        delta = (obj.get("choices") or [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        pass
