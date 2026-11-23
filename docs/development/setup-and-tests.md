---
title: Development setup and tests
order: 1
tags: [development, testing]
---

# Development setup and tests

## Requirements

The package requires Python 3.13 or newer. It has no third-party runtime
dependencies. Tests use pytest, declared in the `test` optional dependency.

## Install and test

From the repository root, install the checkout with its test dependency and
run the suite:

```console
python -m pip install -e ".[test]"
python -m pytest
```

> [!TIP]
> To build the technical documentation without scanning the repository's
> source files, point the CLI at `docs/`: `python -m emdg docs --output docs.html`.

The test modules are organized by package responsibility:

| Test module | Coverage |
| --- | --- |
| `tests/test_frontmatter.py` | Plain Markdown, recognized fields, tags, delimiters, and malformed order values. |
| `tests/test_scanner.py` | Recursive discovery, sorting, section metadata, home page, ignores, drafts, and invalid origins. |
| `tests/test_generator.py` | Serialized output, HTML template behavior, themes, route data, rendering features, and escaping. |
| `tests/test_cli.py` | CLI builds, watcher rebuilds, and server cleanup on interruption. |

## Source tree

```text
emdg/
├── emdg/                 # Installable Python package
│   ├── frontmatter.py    # Metadata parser and Frontmatter dataclass
│   ├── scanner.py        # Filesystem scan and document-tree dataclasses
│   ├── generator.py      # HTML template, JSON serialization, output writer
│   ├── cli.py            # Command-line entry point and runtime modes
│   └── __main__.py       # python -m emdg
├── tests/                # pytest suite grouped by module
├── docs/                 # Markdown used for this generated documentation
├── pyproject.toml        # Build metadata, runtime floor, script, test extra
└── README.md             # Product overview and user quick start
```

## Rebuilding the documentation

The repository's docs are built from the `docs/` directory, not the repository
root, so source code and agent instructions are not scanned:

```console
python -m emdg docs --output docs.html --title "emdg Technical Documentation"
```

The root `docs.html` is generated output and is ignored by Git. Inspect the
generated file after changing documentation to confirm its pages and
distinctive content are present.
