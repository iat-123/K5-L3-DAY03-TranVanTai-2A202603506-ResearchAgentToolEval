---
name: compare_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, fields]
outputs: [fields, rows, item_count, markdown]
side_effect: false
---

Create a Markdown comparison table from two or more items collected by research
tools. Only display requested fields that are present; missing values are shown
as `-`. The date column recognizes `date`, `published_date`, `published_at`,
and `published`. No facts are inferred or fetched.
