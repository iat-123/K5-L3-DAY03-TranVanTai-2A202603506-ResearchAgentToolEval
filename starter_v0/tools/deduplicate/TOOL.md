---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, item_count, removed_count]
side_effect: false
---
# deduplicate

Removes duplicate research items while preserving their original order. URLs
are the primary key; when an item has no URL, its title is used as a fallback.
This tool does not search for or fetch content.
