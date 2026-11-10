from __future__ import annotations

import re
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "reports"


def _error(name: str, message: str) -> dict[str, Any]:
    return {"tool": "export_digest", "error": name, "message": message}


def _safe_stem(filename: str) -> str:
    raw_stem = Path(filename).name
    if raw_stem.casefold().endswith(".md"):
        raw_stem = raw_stem[:-3]
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_stem).strip("._-")
    if not stem or stem in {".", ".."}:
        raise ValueError("filename must contain at least one safe character")
    return stem


def export_markdown_digest(
    content: str,
    filename: str = "research-digest",
    confirmed: bool = False,
) -> dict[str, Any]:
    """Write a confirmed Markdown digest under the fixed local reports directory."""
    if not isinstance(content, str) or not content.strip():
        return _error("ValueError", "content must be a non-empty string")
    if not isinstance(filename, str) or not filename.strip():
        return _error("ValueError", "filename must be a non-empty string")
    if confirmed is not True:
        return _error("confirmation_required", "Confirm the exact digest before saving it")
    try:
        safe_stem = _safe_stem(filename)
    except ValueError as exc:
        return _error("ValueError", str(exc))

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        suffix = 1
        while True:
            candidate_stem = safe_stem if suffix == 1 else f"{safe_stem}-{suffix}"
            output_path = OUTPUT_DIR / f"{candidate_stem}.md"
            try:
                with output_path.open("x", encoding="utf-8", newline="\n") as output_file:
                    output_file.write(content.rstrip() + "\n")
                break
            except FileExistsError:
                suffix += 1
    except OSError as exc:
        return _error(type(exc).__name__, str(exc))
    return {
        "tool": "export_digest",
        "status": "saved",
        "filename": output_path.name,
        "path": str(output_path),
        "bytes_written": output_path.stat().st_size,
    }
