"""Handle long responses: detect truncation and request continuation from the model."""
from __future__ import annotations

import re
from typing import Callable

from .providers.base import ChatMessage


# Common patterns that suggest the model was cut off
TRUNCATION_INDICATORS = (
    r"\.\.\.\s*$",
    r"\s+\.\.\.$",
    r"[,;:\s]+$",  # ends with incomplete punctuation
    r"^$",         # empty (should not continue)
)


def looks_truncated(text: str, min_length: int = 20) -> bool:
    """
    Heuristic: response might be truncated if it ends abruptly (no sentence end)
    or with ellipsis, or is very long and ends mid-sentence.
    """
    if not text or len(text.strip()) < min_length:
        return False
    stripped = text.strip()
    # Ends with sentence terminator
    if re.search(r"[.!?]\s*$", stripped):
        return False
    for pat in TRUNCATION_INDICATORS:
        if re.search(pat, stripped):
            return True
    # Ends with lowercase (mid-sentence) and no final period
    if stripped[-1].islower() and stripped[-1] not in ".!?":
        return True
    return False


def request_continuation(
    get_reply: Callable[[list[ChatMessage]], str],
    messages: list[ChatMessage],
    accumulated: str,
    overlap_chars: int = 500,
    max_continuations: int = 10,
) -> str:
    """
    If accumulated response looks truncated, ask the model to continue.
    get_reply(messages) should return the next chunk. We append a continuation
    prompt with the last overlap_chars of context.
    """
    result = accumulated
    continuations = 0
    while looks_truncated(result) and continuations < max_continuations:
        context = result[-overlap_chars:] if len(result) > overlap_chars else result
        continuation_messages = messages + [
            ChatMessage("assistant", result),
            ChatMessage(
                "user",
                "Continue from where you left off. Do not repeat the previous text. "
                f"Context (last part): {context}"
            ),
        ]
        next_chunk = get_reply(continuation_messages)
        if not next_chunk or next_chunk.strip() in result[-200:]:
            break
        result = result + next_chunk
        continuations += 1
    return result
