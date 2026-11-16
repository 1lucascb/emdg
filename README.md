# emdg

`emdg` (Easy Markdown Docs Generator) scans Markdown files and builds a single
HTML documentation site. It uses convention over configuration: folders become
sections, filenames become page titles, and optional frontmatter customizes
pages and sections.

## Features

- One command to build a searchable, hash-routed documentation site.
- Nested folders become nested sidebar sections.
- Optional frontmatter for page titles, order, descriptions, tags, drafts, and
  section metadata.
- Light, dark, and system-preference themes.
- Custom primary accent colors with contrast-adjusted light/dark variants.
- Optional local HTTP server and automatic rebuild mode.
- No third-party Python runtime dependencies.

## Requirements and installation

Python 3.13 or newer is required.

Install the published package:

```console
pip install emdg
```

Then run it from any directory:

```console
emdg --help
```

To install an editable checkout with the test dependency:

```console
python -m pip install -e ".[test]"
```

## AI agent skill

The [emdg documentation skill](docs/skills/SKILL.md) guides AI agents in
organizing docs and using the CLI, including frontmatter and build workflows.

## Quick start

Given a project like:

```text
my-project/
├── docs/
│   ├── overview.md
│   ├── getting-started/
│   │   ├── _section.md
│   │   ├── install.md
│   │   └── first-steps.md
│   └── reference/
│       └── commands.md
└── ...
```

Build the site:

```console
emdg docs
```

This scans `docs/` and writes `docs.html` to the **current working directory**.
The output location is independent of the source directory. Root-level Markdown
files appear first in the sidebar, except for a root-level `README.md`: it is
the site's home page, opens by default, and is omitted from the sidebar. Clicking
the site title returns to that page. Folders become sections, with deeper folders
becoming subsections.

The page title defaults to the source directory name (`docs` becomes `Docs`).
Filenames and folder names are humanized by replacing hyphens and underscores
with spaces and capitalizing words (`getting-started` becomes `Getting Started`).
Frontmatter can override a Markdown page's display title.

## Command-line reference

```text
emdg [source] [-o OUTPUT] [-t TITLE] [-i NAME]... [--theme auto|light|dark]
     [--primary-color HEX] [--serve] [--watch] [-v]
```

| Option | Default | Description |
| --- | --- | --- |
| `source` | `.` | Directory to scan recursively. It must exist and be a directory. |
| `-o`, `--output` | `docs.html` | Output HTML file. Relative paths are resolved from the current working directory; its parent directory must already exist. |
| `-t`, `--title` | Humanized source directory name | Site title shown in the browser tab and interface. |
| `-i`, `--ignore NAME` | Built-in ignores | Ignore a file or directory by name. Repeat the option for multiple names. Names are matched anywhere in the source tree, not as paths. |
| `--theme` | `auto` | Initial theme: `auto` follows the browser's system preference, or choose `light` or `dark`. A theme already saved in that browser takes precedence. |
| `--primary-color HEX` | `#2563eb` | Primary accent color as `#RGB` or `#RRGGBB`. The generator adjusts it for readable accents in both themes. |
| `--serve` | Off | Serve the generated output on `http://127.0.0.1:8000/<output-filename>` until interrupted. |
| `--watch` | Off | Keep running and rebuild after Markdown files are added, removed, or changed. |
| `-v`, `--verbose` | Off | Print informational messages, including build and watch activity. |
| `-h`, `--help` | — | Show command help. |

Examples:

```console
# Use the current directory and default output
emdg

# Give the site a name and choose the output path
emdg ./docs --output ./public/manual.html --title "Team Handbook"

# Exclude matching names wherever they occur in the source tree
emdg docs --ignore internal --ignore drafts

# Build using a light theme
emdg docs --theme light

# Choose a primary accent color
emdg docs --primary-color "#7c3aed"

# Serve the generated docs and rebuild when Markdown changes
emdg docs --output site.html --serve --watch
```

The server binds to loopback (`127.0.0.1`) on fixed port `8000`; it is intended
for local preview, not as a public hosting server. Without `--watch`, `--serve`
serves the one build made when the command starts. With `--watch`, the CLI checks
for Markdown file changes about twice per second and rebuilds the same output.
Press `Ctrl+C` to stop serving or watching.

The built-in ignored directory names are `.git`, `.hg`, `.svn`, `.venv`, `venv`,
`__pycache__`, `node_modules`, `.idea`, `.vscode`, `dist`, and `build`. Any
dot-prefixed file or directory is also ignored automatically. Custom ignores
are additional name matches; they do not enable scanning hidden files.

The CLI scans `.md` files (case-insensitively). The Python scanning API can use
other extensions.

## Optional frontmatter

Frontmatter is a small YAML-like block at the very top of a Markdown file. It
starts with a line containing `---` and ends with a line containing `---` or
`...`. Everything after the closing line is the Markdown body; the delimiters
are removed before rendering.

```markdown
---
title: Cursor Pagination
emoji: 📄
order: 2
description: How cursor-based pagination works across endpoints.
tags: [api, pagination]
draft: false
---

# Cursor Pagination

Write the page content here.
```

All fields are optional. Without frontmatter, the file is still included and
its title is derived from its filename.

| Field | Type and default | Effect |
| --- | --- | --- |
| `title` | Text; filename-derived title | Overrides the page's sidebar label. It does not add a heading to the Markdown body. |
| `emoji` | Text; none | Prefixes the page's sidebar label. |
| `order` | Integer; `999` | Sorts pages or sections numerically in ascending order. Equal orders are sorted by title, case-insensitively, then by relative path. Lower numbers appear first; omitted or invalid values use `999`. |
| `description` | Text; none | Displays a short description above the page body. |
| `tags` | List of text; empty list | Displays tag badges and includes each tag in sidebar search. |
| `draft` | Boolean-like text; `false` | Excludes the page from the generated site when set to a recognized true value. |

### Frontmatter value syntax

This is a deliberately small parser, not a full YAML implementation:

- Values can be unquoted, single-quoted, or double-quoted. Matching outer
  quotes are removed; YAML escape sequences and nested objects are not parsed.
- `order` must be an integer. A non-integer value leaves the default order
  (`999`) in effect.
- `draft: true`, `draft: yes`, `draft: 1`, and `draft: on` are treated as true,
  case-insensitively. Other values, including `false`, are false.
- Tags can be written inline or as a block list:

  ```yaml
  tags: [api, "getting started"]
  ```

  ```yaml
  tags:
    - api
    - getting started
  ```

- Blank lines and lines beginning with `#` inside the frontmatter are ignored.
- Unknown keys are accepted by the parser but do not change the generated
  documentation.
- If the opening delimiter is missing or there is no closing delimiter, the
  content is treated as ordinary Markdown instead of being partially removed.

### Section metadata files

To customize a folder's sidebar section, put `_section.md` or `index.md` in that
folder and add frontmatter:

```text
docs/
└── getting-started/
    ├── _section.md
    ├── install.md
    └── first-steps.md
```

```markdown
---
title: Start Here
emoji: 🚀
order: 1
description: Installation and first steps.
---

# Start Here

This content appears when the section is selected.
```

The `title`, `emoji`, and `order` values customize the section's sidebar label
and position. `_section.md` takes precedence over `index.md` if both exist.
These helper files are reserved and are not rendered as pages; an `index.md`
body is not used as a landing page. Markdown after `_section.md`'s frontmatter
is displayed as the section's landing content when its sidebar heading is
selected. If `_section.md` has no body, the heading only expands the navigation.
A section's frontmatter description is shown above its landing content when
present. A folder is shown only when it contains at least one non-draft
Markdown page somewhere below it.

## Generated site behavior

- The output is one HTML file containing the scanned Markdown content and
  client-side page data. Navigation changes the URL hash; it does not fetch
  Markdown files after generation.
- The sidebar search filters on page title, Markdown body text, and tags.
- Sidebar sections and subsections are collapsible and start closed. The section
  containing the current page opens automatically; searching opens sections
  with matching results.
- If a section has Markdown body content in `_section.md`, selecting its heading
  displays that content in the main pane as a section landing page.
- The home page footer shows when the site was generated, using a UTC timestamp.
- Pages with `##` or `###` headings get an automatic "On this page" table of
  contents with in-page links.
- GitHub-style blockquote callouts are supported: `[!NOTE]`, `[!TIP]`,
  `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]`. Their styling and the table of
  contents are implemented inline; they add no CDN dependencies.
- The selected page's description and tags appear above its content.
- A custom `--primary-color` supplies the accent hue in both themes. Its light
  and dark variants are adjusted for contrast; the dark theme uses neutral gray
  surfaces.
- A saved theme choice is kept in browser `localStorage` under `emdg-theme`.
  This saved choice takes precedence over the generated `--theme` default.
- Standard Markdown is rendered in the browser by Marked. Fenced code blocks
  are highlighted by Highlight.js; `mermaid` fenced blocks are rendered as
  diagrams by Mermaid.
- Tailwind CSS, Marked, Highlight.js, and Mermaid load from public CDNs. An
  internet connection is required for the complete styling and rendering
  experience.
- The Markdown renderer supports raw HTML. Only build and publish documentation
  from sources you trust.

## Python API

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
    primary_color="#7c3aed",
)
print(output)
```

### `scan_docs`

```python
scan_docs(origin, *, ignore=None, extensions=(".md",))
```

- `origin` is a directory path (`str` or `pathlib.Path`).
- `ignore` is an optional iterable of exact file/directory names to exclude.
  Built-in ignores and the automatic dotfile exclusion still apply.
- `extensions` is an iterable of extensions, with or without the leading dot.
  Matching is case-insensitive.
- Returns a `ScanResult` with an optional root `home` page, other `root_items`,
  and nested `sections`. A root-level `README.md` becomes `home` and is not
  included in `root_items`; a README inside a section remains a normal page.
- Each `DocItem` stores its title, slug, absolute file path, relative path,
  emoji, order, description, and tags. Each `DocSection` stores the
  section metadata, optional Markdown body, items, and subsections.
- Raises `FileNotFoundError` if the origin does not exist and
  `NotADirectoryError` if it is not a directory.

### `generate_html`

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

- `scan_result` is the result of `scan_docs`.
- `output_path` is the HTML file path; its parent directory must exist.
- `title` overrides the site title. By default, the scan root's directory name
  is humanized.
- `theme` must be `auto`, `light`, or `dark`.
- `primary_color` must be a `#RGB` or `#RRGGBB` hex color. The generator
  derives contrast-adjusted accent colors for light and dark backgrounds.
- Writes UTF-8 HTML and returns the resolved output `Path`.

The public package also exports `Frontmatter`, `DocItem`, `DocSection`,
`ScanResult`, `parse_frontmatter`, and `humanize_name`.

## Development

Install the optional test dependency and run the test suite:

```console
python -m pip install -e ".[test]"
python -m pytest
```
