---
title: Command-line interface
order: 2
tags: [cli, operations]
---

# Command-line interface

The `emdg` console script and `python -m emdg` invoke the same CLI.

```text
emdg [source] [-o OUTPUT] [-t TITLE] [-i NAME]... [--theme auto|light|dark]
     [--primary-color HEX] [--serve] [--watch] [-v]
```

| Argument | Default | Behavior |
| --- | --- | --- |
| `source` | `.` | Source directory scanned recursively for `.md` files. |
| `-o`, `--output` | `docs.html` | Output path, resolved relative to the current working directory. Its parent must exist. |
| `-t`, `--title` | Humanized source directory name | Site title shown in the generated interface and browser title. |
| `-i NAME`, `--ignore NAME` | Built-in ignores | Add an exact filename or directory name to ignore. Repeatable; matches at any depth. |
| `--theme` | `auto` | Initial theme: browser preference, `light`, or `dark`. A saved browser choice takes precedence. |
| `--primary-color HEX` | `#2563eb` | Accent hue as `#RGB` or `#RRGGBB`, adjusted for contrast in both themes. |
| `--serve` | Off | Serve the generated file at `http://127.0.0.1:8000/<filename>`. |
| `--watch` | Off | Rebuild after Markdown source files change, without or with `--serve`. |
| `-v` | Off | Increase log verbosity; repeat for debug output. |
| `-h`, `--help` | — | Display command help. |

## Build examples

```console
# Scan docs/ and write docs.html in the current directory
emdg docs

# Choose an output path and site title
emdg docs --output public/manual.html --title "Team Handbook"

# Add names to the default ignore set
emdg docs --ignore internal --ignore drafts

# Build with a dark initial theme
emdg docs --theme dark

# Choose an accent hue for both themes
emdg docs --primary-color "#7c3aed"
```

## Watch and serve

The watcher polls every 0.5 seconds for Markdown file additions, removals, or
changes. Its snapshot tracks relative paths, modification times, and file
sizes. It rebuilds the same output path when the snapshot changes.

The preview server binds only to `127.0.0.1` on fixed port `8000`; it is for
local preview, not public hosting. `--serve` without `--watch` serves only the
initial build. `--watch` without `--serve` rebuilds without starting a server.
Press Ctrl+C to stop either long-running mode.

Source validation and output write `OSError`s, as well as invalid primary
colors, are reported as CLI errors. The scanner's default and hidden-entry
ignore rules are documented in
[Scanning and document model](#/architecture/scanning-and-model).
The dark theme uses neutral gray surfaces; the selected primary color is
adjusted to keep accent text readable on both light and dark backgrounds.
