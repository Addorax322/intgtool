"""Split large texts into chunks that fit within model token limits."""
from __future__ import annotations

from typing import Iterator

# Optional: use tiktoken for accurate token counts (OpenAI/OpenRouter models)
try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False


def estimate_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Estimate token count. Uses tiktoken if available, else ~4 chars per token.
    """
    if _TIKTOKEN_AVAILABLE:
        try:
            enc = tiktoken.get_encoding(encoding_name)
            return len(enc.encode(text))
        except Exception:
            pass
    return (len(text) + 3) // 4


def chunk_text(
    text: str,
    max_tokens: int = 4000,
    overlap_tokens: int = 0,
    encoding_name: str = "cl100k_base",
) -> Iterator[str]:
    """
    Split text into chunks of at most max_tokens. Optional overlap for context.
    Tries to break on paragraph or sentence boundaries when possible.
    """
    if estimate_tokens(text, encoding_name) <= max_tokens:
        yield text
        return

    if _TIKTOKEN_AVAILABLE:
        try:
            enc = tiktoken.get_encoding(encoding_name)
            tokens = enc.encode(text)
            decode = enc.decode
            start = 0
            while start < len(tokens):
                end = min(start + max_tokens, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk = decode(chunk_tokens)
                # Prefer breaking at last paragraph or sentence
                if end < len(tokens) and overlap_tokens <= 0:
                    for sep in ("\n\n", "\n", ". "):
                        idx = chunk.rfind(sep)
                        if idx > max_tokens // 2:
                            chunk = chunk[: idx + len(sep)]
                            # Re-encode to advance start correctly
                            chunk_tokens = enc.encode(chunk)
                            end = start + len(chunk_tokens)
                            break
                yield chunk
                start = end - overlap_tokens if overlap_tokens > 0 else end
            return
        except Exception:
            pass

    # Fallback: character-based (assume ~4 chars per token)
    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end]
        if end < len(text):
            for sep in ("\n\n", "\n", ". "):
                idx = chunk.rfind(sep)
                if idx > max_chars // 2:
                    chunk = chunk[: idx + len(sep)]
                    end = start + len(chunk)
                    break
        yield chunk
        start = end - overlap_chars if overlap_chars > 0 else end
