---
name: emdg-docs
description: Organize, write, and maintain Markdown documentation with the emdg CLI, including its frontmatter, section behavior, generated-site features, Python API, and local preview workflow.
---

# Organize and build documentation with emdg

Use this skill when creating or maintaining a project's documentation and when
building or previewing its site with `emdg`. Treat the repository's current
README, CLI help, and implementation as authoritative if they differ from this
guide.

## What emdg does

`emdg` recursively scans a directory of Markdown files and generates one
HTML file containing the documentation data and client-side navigation. The
generated site does not fetch the Markdown sources after it is built.

- Requires Python 3.13 or newer.
- Has no third-party Python runtime dependencies.
- Installs the `emdg` command from the `emdg.cli:main` entry point.
- Uses Tailwind CSS, Marked, Highlight.js, and Mermaid from public CDNs in the
  generated site. Internet access is needed for the full styling and rendering
  experience.
- Renders raw HTML in Markdown. Build and publish only documentation sources
  that are trusted.

## Workflow

1. Inspect the repository's existing docs, source, and `emdg --help` before
   choosing a structure or documenting behavior. Preserve existing conventions
   and content; make focused edits rather than replacing files wholesale.
2. Keep user-facing documentation in a dedicated `docs/` directory. Pass that
   directory explicitly to the CLI to avoid scanning unrelated Markdown in the
   repository.
3. Use optional frontmatter only when it improves navigation or discovery.
   Keep the page's actual content in the Markdown body.
4. Build from the repository root, then verify the generated HTML includes the
   requested pages and distinctive content. A successful build alone does not
   prove every intended page was included.
5. For CLI or generator code changes, run the relevant tests as well as a build.
6. Report the changed docs and the exact build or preview command.

## Installation and command line

Install the published package:

```console
pip install emdg
```

For development and tests, install the checkout in editable mode with its test
dependency:

```console
python -m pip install -e ".[test]"
```

The command is `emdg`; `emdg --help` displays the live options. The Python
module entry point is also available with `python -m emdg`.

```text
emdg [source] [-o OUTPUT] [-t TITLE] [-i NAME]... [--theme auto|light|dark]
     [--serve] [--watch] [-v]
```

| Argument | Default | Behavior |
| --- | --- | --- |
| `source` | `.` | Directory recursively scanned for Markdown. It must exist and be a directory. |
| `-o`, `--output` | `docs.html` | Output file. Relative paths resolve from the current working directory; the parent directory must already exist. |
| `-t`, `--title` | Humanized source directory name | Site title shown in the generated interface and browser title. This option is optional. |
| `-i NAME`, `--ignore NAME` | Built-in ignores | Ignore a file or directory by exact name anywhere under the source, not by relative path. Repeat to add names. |
| `--theme` | `auto` | Initial theme: `auto` follows the browser preference, or use `light` or `dark`. A theme saved in browser `localStorage` takes precedence. |
| `--serve` | Off | Serve the generated output on loopback at `http://127.0.0.1:8000/<output-filename>`. This is for local preview, not public hosting. |
| `--watch` | Off | Poll for Markdown file additions, removals, or changes about twice per second, then rebuild the same output. |
| `-v` | Off | Increase log verbosity; repeat (`-vv`) for debug logging. |
| `-h`, `--help` | — | Show command help. |

Examples:

```console
# Scan docs/ and write docs.html in the current directory
emdg docs

# Select an output and site title
emdg docs --output public/manual.html --title "Team Handbook"

# Ignore names wherever they occur below docs/
emdg docs --ignore internal --ignore drafts

# Build with a dark initial theme
emdg docs --theme dark

# Serve the built file and rebuild when Markdown changes
emdg docs --output site.html --serve --watch
```

The CLI scans `.md` files case-insensitively. `--watch` can be used without
`--serve` to rebuild without starting a server. `--serve` without `--watch`
serves only the initial build. The server binds to fixed port `8000`; stop the
server or watcher with `Ctrl+C`.

Built-in ignored directory names are `.git`, `.hg`, `.svn`, `.venv`, `venv`,
`__pycache__`, `node_modules`, `.idea`, `.vscode`, `dist`, and `build`. Every
dot-prefixed file or directory is also ignored automatically. Custom ignores
are additive; they do not enable scanning hidden entries.

## Recommended documentation layout

Adapt this structure to the project; do not create empty folders just to match
the example:

```text
repository/
├── docs/
│   ├── README.md
│   ├── getting-started/
│   │   ├── _section.md
│   │   ├── installation.md
│   │   └── first-steps.md
│   ├── guides/
│   │   ├── _section.md
│   │   └── deployment.md
│   └── reference/
│       ├── _section.md
│       └── configuration.md
└── docs.html
```

- Use `docs/README.md` as the home page: it opens by default, is omitted from
  the sidebar, and is shown again when the reader clicks the site title.
  A README inside a subfolder is a normal page.
- Put other root-level pages before sections in the sidebar. Use
  `docs/overview.md` when an overview should be a normal sidebar entry.
- Folder names become section titles; nested folders become subsections.
- A folder is included only if it contains a non-draft Markdown page somewhere
  below it.
- Keep generated HTML outside `docs/` to prevent it being scanned as source.
  The default output is `docs.html` in the current working directory; add it to
  `.gitignore` if it should not be checked in.
- Use descriptive page filenames and verify relative links after moving files.

## Page frontmatter

Frontmatter is optional and must begin at the very start of a Markdown file.
It starts with `---` and ends at the next `---` or `...`. The delimiters are
removed; the remaining text is the Markdown body.

```markdown
---
title: First Steps
emoji: 🚀
order: 1
description: Run the application for the first time.
tags: [setup, beginner]
draft: false
---

# First Steps

Write the page content here.
```

| Field | Default | Effect |
| --- | --- | --- |
| `title` | Humanized filename | Overrides the navigation title; it does not add a heading to the body. |
| `emoji` | None | Prefixes the navigation title. |
| `order` | `999` | Sorts pages or sections numerically; lower values come first. Invalid or omitted values use `999`. Ties sort by title, then relative path. |
| `description` | None | Displays above the page or section body. |
| `tags` | Empty | Shows badges and includes tag text in sidebar search. |
| `draft` | `false` | Excludes the page when set to a recognized true value. |

The parser is intentionally YAML-like, not a complete YAML parser:

- Values may be unquoted or wrapped in matching single or double quotes.
- `order` must parse as an integer.
- `draft: true`, `yes`, `1`, and `on` mean true, case-insensitively. Other values
  mean false.
- Tags accept an inline list (`[api, "getting started"]`) or a block list
  (`- api`). A single scalar tag is accepted too.
- Blank lines and lines beginning with `#` in the frontmatter are ignored.
- Unknown keys are retained in the parser's `extra` mapping but do not affect
  generated output.
- If the opening delimiter is absent or no closing delimiter exists, the whole
  file remains ordinary Markdown; it is not partially stripped.

## Section metadata and landing content

Put `_section.md` or `index.md` in a section folder:

```text
docs/guides/
├── _section.md
├── deployment.md
└── troubleshooting.md
```

```markdown
---
title: Guides
emoji: 🧭
order: 2
description: Practical guides for the team.
---

This Markdown body is the landing content shown when the section is selected.
```

`title`, `emoji`, `order`, and `description` customize the section. `_section.md`
takes precedence over `index.md` when both exist. Both helper filenames are
reserved and are not rendered as pages. An `index.md` body is ignored;
Markdown in `_section.md` is used as the section landing content. If there is
no `_section.md` frontmatter, its content is treated as the body. A section
with an empty body is a navigation-only disclosure. A section description is
shown above a nonempty landing body.

## Generated-site features and rendering

- The sidebar is searchable and contains collapsible sections, initially
  closed. The section containing the active page opens automatically; searching
  opens sections with matches. Search covers page titles, body text, and tags.
- Navigation uses URL hashes; Markdown content is embedded in the generated
  HTML rather than fetched at runtime.
- Pages with `##` or `###` headings get an automatic "On this page" table of
  contents. Links scroll to the heading while preserving the page route.
- GitHub-style blockquote callouts work with these markers (case-insensitive):

  ```markdown
  > [!NOTE]
  > Additional context for the reader.

  > [!WARNING]
  > A risk or important caveat.
  ```

  Supported markers are `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, and `CAUTION`.
  The table of contents and callouts use inline code and add no CDN dependencies.
- Fenced `mermaid` blocks render as diagrams. Fenced code blocks are highlighted
  by Highlight.js; other Markdown is parsed by Marked.
- The home page shows a build-time UTC "Last updated at" timestamp.
- Tailwind CSS, Marked, Highlight.js, and Mermaid load from public CDNs. Without
  network access, the source Markdown is still embedded in the HTML, but page
  rendering and parts of the interface may fail because the HTML does not
  contain pre-rendered Markdown or local copies of those libraries.
- Raw HTML in Markdown is rendered. Only publish content from trusted sources.

## Python API

The public package exports `scan_docs`, `generate_html`, `parse_frontmatter`,
`humanize_name`, and the `Frontmatter`, `DocItem`, `DocSection`, and `ScanResult`
dataclasses.

```python
from emdg import generate_html, scan_docs

result = scan_docs(
    "docs",
    ignore={"internal"},
    extensions={".md", ".markdown"},
)
output = generate_html(
    result,
    "public/docs.html",
    title="Team Handbook",
    theme="dark",
)
```

Key signatures:

```python
scan_docs(origin, *, ignore=None, extensions=(".md",))
generate_html(scan_result, output_path="docs.html", *, title=None, theme="auto")
parse_frontmatter(content)  # -> (Frontmatter, body_without_frontmatter)
```

- `origin` must be a directory. `scan_docs` raises `FileNotFoundError` when it
  does not exist and `NotADirectoryError` when it is not a directory.
- `ignore` accepts exact entry names and adds them to built-in ignores.
- `extensions` accepts extensions with or without a leading dot and matches
  case-insensitively. This lets the Python API scan extensions beyond `.md`.
- `ScanResult` contains `root`, `home`, `root_items`, and nested `sections`.
  A root-level `README.md` becomes `home`, not a root item.
- `DocItem` includes title, slug, absolute and relative paths, emoji, order,
  description, and tags. `DocSection` also includes its child items,
  subsections, and optional landing `body`.
- `generate_html` requires the output parent directory to exist, writes UTF-8
  HTML, and returns the resolved output `Path`. `theme` must be `auto`, `light`,
  or `dark`.

## This repository's local build helper

In this repository, `python build_docs.py` builds the checked-out project's
`docs/` to the root `docs.html`, using the local package source. It is a
repository convenience, not an installed `emdg` CLI option. Run it from any
working directory; its paths are based on the script location.

## Validation and accuracy

- Check `emdg --help` for the installed version's options and inspect the
  implementation when behavior is uncertain. Do not invent flags, frontmatter
  fields, or link-rewriting behavior.
- After documentation changes, run the build and inspect the generated HTML for
  the expected pages and distinctive text.
- For code changes, run the relevant tests; the project's development command
  is `python -m pytest` (or `python -W error -m pytest -q`).
- Avoid starting long-lived `--serve` or `--watch` processes unless requested.
  Stop preview processes after verification.
