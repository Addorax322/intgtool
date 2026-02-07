"""Save AI responses to numbered output files (output_1.txt, output_2.txt, ...)."""
from __future__ import annotations

from pathlib import Path


class OutputManager:
    """Writes responses to output_dir/prefix_N.ext, auto-incrementing N."""

    def __init__(
        self,
        output_dir: str | Path = "./output",
        prefix: str = "output",
        extension: str = ".txt",
    ):
        self.output_dir = Path(output_dir)
        self.prefix = prefix
        self.extension = extension if extension.startswith(".") else f".{extension}"
        self._next_index = 1

    def ensure_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def next_path(self) -> Path:
        """Return path for the next output file (output_1.txt, output_2.txt, ...)."""
        self.ensure_dir()
        path = self.output_dir / f"{self.prefix}_{self._next_index}{self.extension}"
        self._next_index += 1
        return path

    def write_response(self, content: str) -> Path:
        """Write content to the next numbered file; return path."""
        path = self.next_path()
        path.write_text(content, encoding="utf-8")
        return path

    def reset_index(self, start: int = 1) -> None:
        """Reset counter (e.g. for a new run)."""
        self._next_index = start
