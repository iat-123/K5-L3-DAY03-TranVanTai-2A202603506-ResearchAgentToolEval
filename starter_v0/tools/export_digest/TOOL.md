---
name: export_digest
track: bonus
kind: action
requires_env: []
inputs: [content, filename, confirmed]
outputs: [status, filename, path, bytes_written]
side_effect: local_file_write
requires_confirmation: true
---

Save a non-empty Markdown digest into the fixed `starter_v0/reports/` folder.
Only use after the user confirms the exact content. The filename is reduced to
a safe basename; arbitrary paths are never used. Existing files are not
overwritten.
