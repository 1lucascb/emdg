---
title: Scanning and document model
order: 2
tags: [scanner, data model]
---

# Scanning and document model

`scan_docs(origin, *, ignore=None, extensions=(".md",))` in
`emdg.scanner` transforms a directory tree into a `ScanResult`. The model is
deliberately simple: pages and sections hold navigation metadata and source
paths, while page Markdown bodies are loaded later by the generator.

## Result types

- `ScanResult` contains the resolved `root`, an optional root `home`, root
  `root_items`, and top-level `sections`.
- `DocItem` represents one page. It includes a display title, route slug,
  absolute and relative source paths, order, optional emoji and description,
  and tags.
- `DocSection` represents a directory containing included pages somewhere
  below it. It has similar navigation metadata, direct page `items`, nested
  `subsections`, and an optional Markdown landing `body`.

The dataclasses use slots. Lists and dictionaries are created per instance.

## Discovery rules

The source must exist and be a directory; otherwise `scan_docs` raises
`FileNotFoundError` or `NotADirectoryError`. File extensions are normalized to
include a leading dot and matched case-insensitively. The default extension is
`.md`.

Names in `DEFAULT_IGNORE` are excluded at any depth: `.git`, `.hg`, `.svn`,
`.venv`, `venv`, `__pycache__`, `node_modules`, `.idea`, `.vscode`, `dist`, and
`build`. Every dot-prefixed entry is excluded automatically. The `ignore`
argument adds exact file or directory names to this set; it is not a
relative-path filter and cannot re-enable hidden entries.

Markdown files are read as UTF-8. Files marked `draft: true` are excluded.
Directories are retained as sections only if recursive scanning finds at least
one included page below them, so empty and draft-only sections disappear.
`_section.md` and `index.md` are reserved section metadata filenames and are
not emitted as pages.

## Titles, routes, and ordering

Without a `title`, file and directory names are humanized by replacing hyphens
and underscores with spaces and capitalizing each word. A page slug is its
source-relative path with its final extension removed and separators
normalized to `/`; for example, `guides/first-steps.md` becomes
`guides/first-steps`.

Pages and sections at each level sort independently by ascending numeric
`order`, then case-insensitive title, then relative path. The default order is
`999`. A root-level `README.md` (case-insensitive filename match) becomes the
home page and is removed from `root_items`. A README in a subdirectory remains
a normal page.

## Section metadata selection

For each retained directory, `_section.md` is checked before `index.md`.
Metadata from the first existing helper file overrides the section defaults.
Only `_section.md` contributes a landing body; `index.md` body text is ignored.
The helper's body is the text after any recognized frontmatter delimiters.

See [Frontmatter format](#/reference/frontmatter-format) for parser behavior
and supported fields.
