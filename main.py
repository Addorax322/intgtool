#!/usr/bin/env python3
"""
CLI entry point for the AI Integration Tool.
Usage:
  python main.py                         # interactive chat
  python main.py "Your prompt"            # single prompt, output to file
  python main.py -i request.txt -o result.txt   # input from file, full result to one file
  python main.py --file input.txt        # same as -i; uses request_response.txt if no -o
  python main.py --stream "Prompt"       # stream response to stdout and save to file
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root so "ai_integration_tool" is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai_integration_tool.orchestrator import AIOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Integration Tool: multi-provider API with chunking, continuation, and streaming."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Single prompt (optional; without it, runs interactive chat).",
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="Read your request from this .txt file (long text is chunked automatically).",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Write the full AI response to this .txt file (use with --input).",
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        default=None,
        help="Same as --input: read request from this .txt file.",
    )
    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="Stream response to stdout (when supported by model).",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Model ID (e.g. deepseek/deepseek-chat, yandexgpt/latest).",
    )
    parser.add_argument(
        "--provider", "-p",
        type=str,
        default=None,
        choices=["openrouter", "yandex_gpt"],
        help="Force a specific provider.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save response to output_N.txt.",
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=None,
        help="Path to config YAML (default: config.yaml or config.example.yaml).",
    )
    args = parser.parse_args()

    from ai_integration_tool.config_loader import load_config
    config_path = str(args.config) if args.config else None
    orch = AIOrchestrator(config=load_config(config_path))

    # Input from file: --input / --file (file takes precedence for backward compat)
    input_file = args.input or args.file
    if input_file is not None:
        if not input_file.exists():
            print(f"Error: file not found: {input_file}", file=sys.stderr)
            sys.exit(1)
        text = input_file.read_text(encoding="utf-8")
        if not text.strip():
            print("Error: input file is empty.", file=sys.stderr)
            sys.exit(1)
        # Output path: explicit --output, or default: {input_stem}_response.txt
        output_file = args.output
        if output_file is None:
            output_file = input_file.with_name(f"{input_file.stem}_response.txt")
        output_file = output_file.resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        # Process (chunk if long), combine all responses into one and write to output file
        responses = orch.process_text(
            text,
            model=args.model,
            provider=args.provider,
            stream=False,
            save_each_chunk=False,  # we write one combined file
            auto_continue=True,
        )
        combined = "\n\n---\n\n".join(responses) if len(responses) > 1 else (responses[0] if responses else "")
        output_file.write_text(combined, encoding="utf-8")
        print(f"Processed {len(responses)} chunk(s). Full response written to: {output_file}")
        return

    if args.prompt is not None:
        if args.stream:
            from ai_integration_tool.providers.base import ChatMessage
            messages = [ChatMessage("user", args.prompt)]
            result = orch._chat_with_fallback(
                messages,
                model=args.model or orch.default_model,
                provider=args.provider,
                stream=True,
            )
            if isinstance(result, str):
                print(result, end="")
                full_reply = result
            else:
                chunks = []
                for chunk in result:
                    chunks.append(chunk)
                    print(chunk, end="", flush=True)
                print()
                full_reply = "".join(chunks)
            if not args.no_save:
                p = orch.output.write_response(full_reply)
                print(f"Saved to {p}", file=sys.stderr)
        else:
            reply = orch.chat(
                args.prompt,
                model=args.model,
                provider=args.provider,
                stream=False,
                save_to_file=not args.no_save,
            )
            print(reply)
        return

    # Interactive chat
    print("AI Integration Tool – interactive chat. Type 'exit' or 'quit' to end.\n")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user or user.lower() in ("exit", "quit"):
            print("Bye.")
            break
        try:
            reply = orch.chat(
                user,
                model=args.model,
                provider=args.provider,
                stream=args.stream,
                save_to_file=False,
            )
            print(f"Assistant: {reply}\n")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
