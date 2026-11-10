from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def _error(message: str) -> dict[str, Any]:
    return {"tool": "filter_results", "error": "ValueError", "message": message}


def _item_text(item: dict[str, Any]) -> str:
    return " ".join(
        str(value)
        for key, value in item.items()
        if key in {"title", "summary", "source", "url"} and isinstance(value, str)
    ).casefold()


def _valid_string_list(value: Any, name: str) -> list[str] | dict[str, Any]:
    if value is None:
        return []
    if not isinstance(value, list) or any(
        not isinstance(entry, str) or not entry.strip() for entry in value
    ):
        return _error(f"{name} must be a list of non-empty strings")
    return [entry.strip().casefold() for entry in value]


def filter_research_results(
    items: list[dict[str, Any]] | None = None,
    include_terms: list[str] | None = None,
    exclude_terms: list[str] | None = None,
    domains: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Filter existing research results without changing their order or contents."""
    if items is not None and not isinstance(items, list):
        return _error("items must be a list of objects")
    items = items or []
    if any(not isinstance(item, dict) for item in items):
        return _error("every item must be an object")

    included = _valid_string_list(include_terms, "include_terms")
    if isinstance(included, dict):
        return included
    excluded = _valid_string_list(exclude_terms, "exclude_terms")
    if isinstance(excluded, dict):
        return excluded
    domain_filters = _valid_string_list(domains, "domains")
    if isinstance(domain_filters, dict):
        return domain_filters
    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, int) or limit < 1
    ):
        return _error("limit must be a positive integer")

    filtered: list[dict[str, Any]] = []
    for item in items:
        text = _item_text(item)
        if included and not all(term in text for term in included):
            continue
        if excluded and any(term in text for term in excluded):
            continue
        if domain_filters:
            url = item.get("url")
            try:
                hostname = urlsplit(url).hostname if isinstance(url, str) else None
            except ValueError:
                hostname = None
            host = hostname.casefold() if hostname else None
            if not host or not any(
                host == domain or host.endswith(f".{domain}")
                for domain in domain_filters
            ):
                continue
        filtered.append(item)

    if limit is not None:
        filtered = filtered[:limit]
    return {
        "tool": "filter_results",
        "items": filtered,
        "item_count": len(filtered),
        "removed_count": len(items) - len(filtered),
    }
