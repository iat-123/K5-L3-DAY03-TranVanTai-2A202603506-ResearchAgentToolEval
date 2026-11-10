from __future__ import annotations

from typing import Any


ALLOWED_FIELDS = {"title", "source", "date", "url", "summary"}
DATE_FIELDS = ("date", "published_date", "published_at", "published")


def _error(message: str) -> dict[str, Any]:
    return {"tool": "compare_sources", "error": "ValueError", "message": message}


def _field_value(item: dict[str, Any], field: str) -> str:
    keys = DATE_FIELDS if field == "date" else (field,)
    for key in keys:
        value = item.get(key)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", "<br>")
    return "-"


def compare_research_sources(
    items: list[dict[str, Any]] | None = None,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Build a factual comparison table from fields present in collected items."""
    if not isinstance(items, list) or len(items) < 2:
        return _error("items must contain at least two objects")
    if any(not isinstance(item, dict) for item in items):
        return _error("every item must be an object")
    fields = fields or ["title", "source", "date", "url"]
    if (
        not isinstance(fields, list)
        or not fields
        or any(not isinstance(field, str) or field not in ALLOWED_FIELDS for field in fields)
    ):
        return _error(f"fields must be a non-empty list from {sorted(ALLOWED_FIELDS)}")
    if len(fields) != len(set(fields)):
        return _error("fields must not contain duplicates")

    headers = ["#", *fields]
    rows = [
        {"index": index, **{field: _field_value(item, field) for field in fields}}
        for index, item in enumerate(items, start=1)
    ]
    markdown_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    markdown_lines.extend(
        "| " + " | ".join([str(row["index"]), *(row[field] for field in fields)]) + " |"
        for row in rows
    )
    return {
        "tool": "compare_sources",
        "fields": fields,
        "rows": rows,
        "item_count": len(rows),
        "markdown": "\n".join(markdown_lines),
    }
