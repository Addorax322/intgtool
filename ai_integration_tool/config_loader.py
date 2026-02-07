"""Load and validate configuration from YAML and environment."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load config from YAML. If config_path is set, load that file; else use config.yaml then config.example.yaml."""
    base = Path(__file__).resolve().parent.parent
    if config_path is not None:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            return _apply_env_overrides(cfg)
        return _apply_env_overrides({})
    for name in ("config.yaml", "config.example.yaml"):
        path = base / name
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            return _apply_env_overrides(cfg)
    return _apply_env_overrides({})


def _apply_env_overrides(cfg: dict[str, Any]) -> dict[str, Any]:
    """Inject API keys and folder_id from environment if present."""
    providers = cfg.get("providers", {})
    env_map = {
        "openrouter": "OPENROUTER_API_KEY",
        "yandex_gpt": "YANDEX_API_KEY",
    }
    for provider_id, env_var in env_map.items():
        if provider_id in providers and os.environ.get(env_var):
            if not isinstance(providers[provider_id], dict):
                providers[provider_id] = {}
            providers[provider_id]["api_key"] = os.environ[env_var]
    if "yandex_gpt" in providers and os.environ.get("YANDEX_FOLDER_ID"):
        if not isinstance(providers["yandex_gpt"], dict):
            providers["yandex_gpt"] = {}
        providers["yandex_gpt"]["folder_id"] = os.environ["YANDEX_FOLDER_ID"]
    cfg["providers"] = providers
    return cfg
