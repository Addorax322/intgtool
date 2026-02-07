"""
Main orchestrator: chunking, provider fallback, retries, continuation, streaming, output.
"""
from __future__ import annotations

from typing import Iterator

from .chunking import chunk_text, estimate_tokens
from .config_loader import load_config
from .continuation import request_continuation
from .output_manager import OutputManager
from .providers import get_provider
from .providers.base import ChatMessage, ProviderError
from .retry import with_retry


def _is_retryable(e: Exception) -> bool:
    if isinstance(e, (ProviderError, TimeoutError, ConnectionError)):
        return True
    if hasattr(e, "response") and getattr(e, "response") is not None:
        status = getattr(getattr(e, "response"), "status_code", None)
        if status in (429, 500, 502, 503, 504):
            return True
    return False


class AIOrchestrator:
    """
    Single entry point: process long texts with chunking, use multiple providers
    with fallback, retries, continuation, and optional streaming; save to files.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or load_config()
        self.max_input_tokens = self.config.get("max_input_tokens", 4000)
        self.max_output_tokens = self.config.get("max_output_tokens", 4096)
        self.continuation_overlap = self.config.get("continuation_overlap", 200)
        retry_cfg = self.config.get("retry", {})
        self.retry_attempts = retry_cfg.get("max_attempts", 3)
        self.timeout = retry_cfg.get("timeout_seconds", 120)
        out_cfg = self.config.get("output", {})
        self.output = OutputManager(
            output_dir=out_cfg.get("directory", "./output"),
            prefix=out_cfg.get("filename_prefix", "output"),
            extension=out_cfg.get("extension", ".txt"),
        )
        self.fallback_providers = self.config.get("fallback_providers", ["openrouter"])
        self.default_provider = self.config.get("default_provider", "openrouter")
        self.default_model = self.config.get("default_model", "deepseek/deepseek-chat")

    def _get_provider(self, provider_name: str | None = None):
        name = provider_name or self.default_provider
        providers_cfg = self.config.get("providers", {})
        prov_cfg = providers_cfg.get(name, {})
        if not prov_cfg.get("enabled", True):
            raise ProviderError(f"Provider {name} is disabled")
        return get_provider(name, prov_cfg)

    def _model_for_provider(self, provider_name: str, requested_model: str) -> str:
        """Return a model ID that this provider supports; fall back to provider's first model."""
        models = self.config.get("providers", {}).get(provider_name, {}).get("models", [])
        model_ids = []
        for m in models:
            if isinstance(m, dict) and "id" in m:
                model_ids.append(m["id"])
            elif isinstance(m, str):
                model_ids.append(m)
        if requested_model in model_ids:
            return requested_model
        if model_ids:
            return model_ids[0]
        return requested_model

    def _chat_with_fallback(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        provider: str | None = None,
        stream: bool = False,
    ) -> str | Iterator[str]:
        model = model or self.default_model
        providers_to_try = [provider] if provider else self.fallback_providers
        providers_to_try = [p for p in providers_to_try if self.config.get("providers", {}).get(p, {}).get("enabled", True)]
        last_error: Exception | None = None
        for prov_name in providers_to_try:
            try:
                prov = self._get_provider(prov_name)
                model_for_prov = self._model_for_provider(prov_name, model)
                if stream and not prov.supports_streaming(model_for_prov):
                    stream = False
                result = with_retry(
                    lambda: prov.chat(
                        messages,
                        model=model_for_prov,
                        max_tokens=self.max_output_tokens,
                        stream=stream,
                    ),
                    max_attempts=self.retry_attempts,
                    timeout=self.timeout,
                    is_retryable=_is_retryable,
                )
                return result
            except Exception as e:
                last_error = e
                continue
        raise last_error or ProviderError("All providers failed")

    def process_text(
        self,
        text: str,
        system_prompt: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        stream: bool = False,
        save_each_chunk: bool = True,
        auto_continue: bool = True,
    ) -> list[str]:
        """
        Chunk long text, call AI for each chunk (with fallback and retries),
        optionally continue truncated replies, stream if supported, save to files.
        Returns list of full responses (one per chunk).
        """
        chunks = list(chunk_text(text, max_tokens=self.max_input_tokens))
        all_responses: list[str] = []
        for i, chunk in enumerate(chunks):
            messages = []
            if system_prompt:
                messages.append(ChatMessage("system", system_prompt))
            messages.append(ChatMessage("user", chunk))

            def get_reply(msgs: list[ChatMessage]) -> str:
                out = self._chat_with_fallback(msgs, model=model, provider=provider, stream=False)
                return out if isinstance(out, str) else "".join(out)

            raw = with_retry(
                lambda: get_reply(messages),
                max_attempts=self.retry_attempts,
                timeout=self.timeout,
                is_retryable=_is_retryable,
            )
            if auto_continue:
                raw = request_continuation(
                    get_reply,
                    messages,
                    raw,
                    overlap_chars=self.continuation_overlap * 4,
                )
            all_responses.append(raw)
            if save_each_chunk:
                self.output.write_response(raw)
        return all_responses

    def chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        stream: bool = False,
        save_to_file: bool = True,
        auto_continue: bool = True,
    ) -> str:
        """
        Single prompt (no chunking). Optionally stream, save to file, and auto-continue.
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage("system", system_prompt))
        messages.append(ChatMessage("user", prompt))

        result = self._chat_with_fallback(messages, model=model, provider=provider, stream=stream)
        if isinstance(result, str):
            full = result
        else:
            full = "".join(result)

        if auto_continue and not stream:
            def get_reply(msgs: list[ChatMessage]) -> str:
                out = self._chat_with_fallback(msgs, model=model, provider=provider, stream=False)
                return out if isinstance(out, str) else "".join(out)
            full = request_continuation(get_reply, messages, full, overlap_chars=self.continuation_overlap * 4)

        if save_to_file:
            self.output.write_response(full)
        return full
