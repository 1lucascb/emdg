---
title: System overview
order: 1
tags: [architecture, data flow]
---

# System overview

## Package boundaries

| Module | Responsibility |
| --- | --- |
| `emdg.frontmatter` | Defines `Frontmatter` and parses the supported YAML-like metadata block. |
| `emdg.scanner` | Walks a source directory, applies ignore and draft rules, and constructs `ScanResult`, `DocItem`, and `DocSection` objects. |
| `emdg.generator` | Serializes the scan tree, embeds it into the HTML template, and writes the generated file. |
| `emdg.cli` | Parses command-line arguments and coordinates generation, watching, and local serving. |
| `emdg.__main__` | Makes `python -m emdg` invoke the CLI. |
| `emdg.__init__` | Re-exports the supported Python API. |

`pyproject.toml` declares the `emdg` console script as
`emdg.cli:main`. The project has no runtime dependencies; pytest is an optional
development dependency.

## Build-time data flow

1. The CLI resolves the source and output paths and combines built-in ignores
   with `--ignore` names.
2. `scan_docs` validates the source directory and recursively builds the
   document tree. It reads frontmatter to decide page titles, metadata, and
   draft inclusion. It reads `_section.md` body text for section landing
   content.
3. `generate_html` reads each included page's Markdown body, constructs a JSON
   payload, and injects it and the site settings into the HTML template.
4. The completed UTF-8 HTML is written to the output path. The output's parent
   directory must already exist.
5. In a browser, JavaScript reads the embedded payload and handles navigation,
   search, theme selection, and Markdown rendering.

The generated site does not fetch Markdown files at runtime. Rebuild the HTML
after editing its source documents.

## Entry points

Use the installed command:

```console
emdg docs --output docs.html --title "Team Docs"
```

Or invoke the module:

```console
python -m emdg docs --output docs.html --title "Team Docs"
```

The Python entry point `main(argv)` is also callable directly and returns an
integer exit code on successful execution.
