---
title: Python API
order: 1
tags: [api, python]
---

# Python API

The package root re-exports its supported types and functions:

```python
from emdg import (
    DocItem,
    DocSection,
    Frontmatter,
    ScanResult,
    generate_html,
    humanize_name,
    parse_frontmatter,
    scan_docs,
)
```

## `scan_docs`

```python
scan_docs(origin, *, ignore=None, extensions=(".md",))
```

`origin` accepts a string or `pathlib.Path`. `ignore` is an optional iterable
of exact entry names, additive to the built-in ignores and automatic
dot-prefixed-entry exclusion. `extensions` is an iterable of extensions, with
or without a leading dot, matched without regard to case.

The function returns a `ScanResult`. A root `README.md` becomes `home`; other
root pages are in `root_items`; subdirectories with published pages become
nested `DocSection` objects. It raises `FileNotFoundError` for a missing origin
and `NotADirectoryError` when the origin is not a directory.

## `generate_html`

```python
generate_html(
    scan_result,
    output_path="docs.html",
    *,
    title=None,
    theme="auto",
    primary_color="#2563eb",
)
```

`scan_result` is a `ScanResult`. `output_path` defaults to `docs.html`; its
parent directory must exist. `title` overrides the humanized source directory
name. `theme` must be `auto`, `light`, or `dark`. `primary_color` accepts a
`#RGB` or `#RRGGBB` hex value and determines contrast-adjusted accents for both
themes. The function writes UTF-8 HTML and returns the resolved output `Path`.

## Other public helpers

```python
parse_frontmatter(content)  # -> (Frontmatter, body_without_frontmatter)
humanize_name(name)          # -> str
```

`parse_frontmatter` returns default metadata and the original content when the
opening or closing delimiter is missing. `humanize_name` replaces hyphens and
underscores with spaces, then capitalizes each word.

The data classes are `Frontmatter`, `DocItem`, `DocSection`, and `ScanResult`.
Their fields are described in [Scanning and document model](#/architecture/scanning-and-model).
