---
name: extract_links
track: core
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [links, count]
side_effect: false
---
# extract_links

Extracts unique HTTP and HTTPS URLs from user-provided text in their original order. It does not open URLs or search the web.
