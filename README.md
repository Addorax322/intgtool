# AI Integration Tool

A configurable, API-based system that interfaces with multiple AI providers (OpenRouter, etc.), with chunking, auto-continuation, retries, and optional streaming.

## Features

- **Multiple AI providers**: OpenRouter (DeepSeek, Qwen, Mistral, etc.) out of the box; easy to add more.
- **Chunking**: Splits large input texts into token-sized chunks so they fit model limits.
- **Long response handling**: Detects truncated replies and automatically requests continuation while keeping context.
- **Error handling & retries**: Configurable retries with exponential backoff and timeouts; fallback to the next provider if one fails.
- **Output management**: Saves responses to `output_1.txt`, `output_2.txt`, etc., in a configurable directory.
- **Streaming**: Real-time streaming for providers that support it (e.g. OpenRouter).
- **Flexible config**: YAML config and environment variables for API keys and model settings.

## Setup

### Запуск на другом компьютере (скачать с GitHub)

1. **Установите Python** (3.9+) и Git, если их ещё нет.
2. **Скачайте проект** (клонирование репозитория):

   ```bash
   git clone https://github.com/Addorax322/intgtool.git
   cd intgtool
   ```

3. Дальше — как в разделе Setup ниже: создайте venv, установите зависимости, скопируйте `config.example.yaml` в `config.yaml` и задайте API-ключи (или переменные окружения).
4. **Запуск**: `python main.py "ваш запрос"` или `python main.py --input request.txt --output result.txt`.

---

1. **Clone or copy** the project and create a virtual environment:

   ```bash
   cd ai-integration-tool
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**:

   - Copy `config.example.yaml` to `config.yaml`.
   - Set API keys via environment variables (recommended) or in `config.yaml`:
     - **OpenRouter**: `OPENROUTER_API_KEY` — get keys at [OpenRouter Settings](https://openrouter.ai/settings/keys).

## Usage

- **Single prompt** (response saved to `output/output_1.txt` by default):

  ```bash
  python main.py "Explain quantum computing in simple terms"
  ```

- **Stream response** to stdout and save to file:

  ```bash
  python main.py --stream "Write a short poem about code"
  ```

- **Request from a file, result to a file** (long requests are chunked automatically; full response goes to one .txt file):

  ```bash
  python main.py --input request.txt --output result.txt
  ```
  If you omit `--output`, the result is written to `request_response.txt` (same folder as the input). You can use `-i` and `-o` as short options; `--file` is the same as `--input`.

- **Interactive chat** (no file argument, no prompt):

  ```bash
  python main.py
  ```

- **Options**:
  - `--model`, `-m`: Model ID (e.g. `deepseek/deepseek-r1`).
  - `--provider`, `-p`: Force provider: `openrouter`.
  - `--no-save`: Do not write output files.
  - `--config`, `-c`: Path to config YAML.

## Configuration (config.yaml)

- **default_provider** / **default_model**: Used when you don’t pass `--provider` or `--model`.
- **fallback_providers**: List of provider names to try in order if one fails.
- **max_input_tokens**, **max_output_tokens**: For chunking and completion limits.
- **retry**: `max_attempts`, `timeout_seconds`, delays.
- **output**: `directory`, `filename_prefix`, `extension` for saved files.
- **providers**: Per-provider `base_url`, `models` (with `id` and `supports_streaming`), and optional `api_key` (or use env vars).

## Adding a New Provider

1. In `ai_integration_tool/providers/`, add a new class that extends `BaseProvider` and implements `chat()` (and optionally `supports_streaming()`).
2. Register it in `providers/__init__.py` in `PROVIDER_REGISTRY`.
3. Add settings and models in `config.yaml` under `providers.<name>`.

## Project layout

```
ai-integration-tool/
├── config.example.yaml    # Example config (copy to config.yaml)
├── main.py                # CLI entry point
├── requirements.txt
├── README.md
└── ai_integration_tool/
    ├── __init__.py
    ├── config_loader.py   # Load YAML + env
    ├── retry.py           # Retries and timeouts
    ├── chunking.py        # Text chunking by tokens
    ├── continuation.py   # Truncation detection and continuation
    ├── output_manager.py  # output_1.txt, output_2.txt, ...
    ├── orchestrator.py    # Ties providers, chunking, retries, output
    └── providers/
        ├── base.py        # Abstract provider
        └── openrouter.py
```

## License

Use and modify as needed for your project.
