# emdg technical documentation

This documentation describes the implementation and public interfaces of
`emdg` (Easy Markdown Docs Generator). It is intended for developers integrating
the package, maintaining its source, or investigating how a Markdown tree
becomes a standalone HTML documentation site.

## What the project does

`emdg` reads Markdown files from a source directory, parses optional
frontmatter, arranges pages into a section tree, and writes one HTML file.
Markdown source text is embedded in the output as data; the browser renders it
and handles navigation without requesting the source files.

The Python runtime has no third-party dependencies and requires Python 3.13 or
newer. The generated page loads Tailwind CSS, Marked, Highlight.js, and Mermaid
from public CDNs.

## Documentation map

- [Architecture overview](#/architecture/system-overview) follows the package
  modules and build-time/runtime data flow.
- [Scanning and document model](#/architecture/scanning-and-model) describes
  discovery rules, ordering, section construction, and the model dataclasses.
- [HTML generation](#/architecture/html-generation) covers serialization,
  templating, routing, rendering, and external browser dependencies.
- [Python API](#/reference/python-api) documents the package's public exports
  and call signatures.
- [Command-line interface](#/reference/cli) describes arguments, build,
  watching, and local serving.
- [Frontmatter format](#/reference/frontmatter-format) specifies the supported
  metadata syntax and section helper files.
- [Development and tests](#/development/setup-and-tests) explains local
  setup, test coverage, and the repository layout.
- [GitHub Pages deployment](#/development/github-pages) explains the
  deployment workflow and the repository setting it requires.

The existing [agent skill](#/skills/SKILL) is also included in the generated
site as an independent docs page.

## Build this documentation

From the repository root, run:

```console
python -m emdg docs --output docs.html --title "emdg Technical Documentation"
```

The output is written at the repository root, outside the Markdown source
directory. Open `docs.html` in a browser; internet access is needed for the
site's CDN-hosted rendering libraries and styles.

The repository's GitHub Actions workflow deploys the same docs source to
GitHub Pages when changes are pushed to `main`. See
[GitHub Pages deployment](#/development/github-pages) for setup details.
