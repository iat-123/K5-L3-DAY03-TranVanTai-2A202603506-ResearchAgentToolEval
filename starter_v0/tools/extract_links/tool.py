from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TRAILING_PUNCTUATION = ".,;:!?)]}"


def extract_links(text: str = "") -> dict[str, Any]:
    try:
        links: list[str] = []
        seen: set[str] = set()
        for match in _URL_PATTERN.finditer(text):
            candidate = match.group(0).rstrip(_TRAILING_PUNCTUATION)
            parsed = urlsplit(candidate)
            if not parsed.netloc or candidate in seen:
                continue
            seen.add(candidate)
            links.append(candidate)
        return {"tool": "extract_links", "links": links, "count": len(links)}
    except Exception as exc:
        return err("extract_links", exc)
