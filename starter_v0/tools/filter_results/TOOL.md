---
name: filter_results
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, include_terms, exclude_terms, domains, limit]
outputs: [items, item_count, removed_count]
side_effect: false
---

Filter results already collected by another research tool. All include terms
must match; any exclude term removes an item. Domain filters match the exact
host or its subdomains. The tool preserves input order and item contents.
