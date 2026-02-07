"""YandexGPT API provider (Yandex Cloud Foundation Models)."""
from __future__ import annotations

import json
from typing import Iterator

import requests

from .base import BaseProvider, ChatMessage, ProviderError


class YandexGPTProvider(BaseProvider):
    """
    Yandex Cloud Foundation Models (YandexGPT).
    Requires IAM token or API key in config; set YANDEX_API_KEY env var or api_key in config.
    Model URI format: gpt://{folder_id}/yandexgpt/latest
    """

    name = "yandex_gpt"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = (
            config.get("base_url", "https://llm.api.cloud.yandex.net/foundationModels/v1")
            .rstrip("/")
        )
        self.api_key = config.get("api_key", "")
        self.folder_id = config.get("folder_id", "")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _model_uri(self, model: str) -> str:
        # Already a full URI (e.g. gpt://folder-id/yandexgpt/latest)
        if model.startswith("gpt://"):
            return model
        # Model from another provider (e.g. deepseek/deepseek-chat) — use our first configured model
        if not model.startswith("yandexgpt"):
            models = self.config.get("models", [])
            model = next(
                (m["id"] for m in models if isinstance(m, dict) and "id" in m),
                "yandexgpt/latest",
            )
        # id like "yandexgpt/latest" -> gpt://{folder_id}/yandexgpt/latest
        if not self.folder_id:
            raise ProviderError(
                "YandexGPT requires folder_id in config (or YANDEX_FOLDER_ID env). "
                "Set it in config.yaml under providers.yandex_gpt.folder_id"
            )
        return f"gpt://{self.folder_id}/{model}"

    def _payload(self, messages: list[ChatMessage], model: str, max_tokens: int, stream: bool) -> dict:
        return {
            "modelUri": self._model_uri(model),
            "completionOptions": {
                "maxTokens": str(max_tokens),
                "stream": stream,
            },
            "messages": [{"role": m.role, "text": m.content} for m in messages],
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
        url = f"{self.base_url}/completion"
        payload = self._payload(messages, model, max_tokens, stream)
        if stream:
            return self._stream(url, payload)
        return self._complete(url, payload)

    def _complete(self, url: str, payload: dict) -> str:
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=120)
        if resp.status_code != 200:
            raise ProviderError(f"YandexGPT API error {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data.get("result", {})
        alternatives = result.get("alternatives", [{}])
        return alternatives[0].get("message", {}).get("text", "") if alternatives else ""

    def _stream(self, url: str, payload: dict) -> Iterator[str]:
        with requests.post(
            url, headers=self._headers(), json=payload, stream=True, timeout=120
        ) as resp:
            if resp.status_code != 200:
                raise ProviderError(f"YandexGPT API error {resp.status_code}: {resp.text[:500]}")
            for line in resp.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8").strip()
                try:
                    obj = json.loads(line_str)
                    chunk = obj.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
                    if chunk:
                        yield chunk
                except json.JSONDecodeError:
                    pass
