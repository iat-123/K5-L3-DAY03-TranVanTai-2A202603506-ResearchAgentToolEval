from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _normalized_url(value: str) -> str:
    parts = urlsplit(value.strip())
    if not parts.scheme and not parts.netloc:
        return value.strip().casefold()
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), path, parts.query, ""))


def _normalized_title(value: str) -> str:
    return " ".join(value.split()).casefold()


def deduplicate_items(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item for each URL, falling back to title when URL is absent."""
    if items is not None and not isinstance(items, list):
        return {
            "tool": "deduplicate",
            "error": "ValueError",
            "message": "items must be a list of objects",
        }
    items = items or []
    if any(not isinstance(item, dict) for item in items):
        return {
            "tool": "deduplicate",
            "error": "ValueError",
            "message": "every item must be an object",
        }

    unique_items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for item in items:
        url = item.get("url")
        if isinstance(url, str) and url.strip():
            key = ("url", _normalized_url(url))
        else:
            title = item.get("title")
            normalized_title = _normalized_title(title) if isinstance(title, str) else ""
            if not normalized_title:
                unique_items.append(item)
                continue
            key = ("title", normalized_title)

        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return {
        "tool": "deduplicate",
        "items": unique_items,
        "item_count": len(unique_items),
        "removed_count": len(items) - len(unique_items),
    }
