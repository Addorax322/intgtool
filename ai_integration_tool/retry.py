"""Retry logic with exponential backoff and timeout handling."""
from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 3,
    min_delay: float = 1.0,
    max_delay: float = 30.0,
    timeout: float | None = None,
    is_retryable: Callable[[Exception], bool] | None = None,
) -> T:
    """
    Execute fn with exponential backoff. Optionally enforce a timeout per attempt.
    """
    last_exc: Exception | None = None
    delay = min_delay
    for attempt in range(1, max_attempts + 1):
        try:
            if timeout is not None and timeout > 0:
                return _run_with_timeout(fn, timeout)
            return fn()
        except Exception as e:
            last_exc = e
            if is_retryable is not None and not is_retryable(e):
                raise
            if attempt == max_attempts:
                raise
            time.sleep(delay)
            delay = min(delay * 2, max_delay)
    raise last_exc or RuntimeError("Retry exhausted")


def _run_with_timeout(fn: Callable[[], T], timeout: float) -> T:
    """Run fn in a single attempt; timeout is best-effort (thread-based would be better)."""
    import threading
    result: list[T] = []
    exc: list[Exception] = []

    def target() -> None:
        try:
            result.append(fn())
        except Exception as e:
            exc.append(e)

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        raise TimeoutError(f"Operation timed out after {timeout}s")
    if exc:
        raise exc[0]
    return result[0]
