---
title: Frontmatter format
order: 3
tags: [metadata, markdown]
---

# Frontmatter format

Frontmatter is an optional YAML-like metadata block at the very beginning of a
Markdown file. It starts with a line containing `---` and ends at the next line
containing `---` or `...`. The delimiters and metadata are removed from the
body. If the opening delimiter or a closing delimiter is absent, the entire
file is treated as ordinary Markdown.

```markdown
---
title: Cursor Pagination
emoji: 📄
order: 2
description: How cursor-based pagination works.
tags: [api, "getting started"]
draft: false
---

# Cursor Pagination

Page content begins after the closing delimiter.
```

## Page fields

| Field | Default | Effect |
| --- | --- | --- |
| `title` | Humanized filename | Overrides the navigation title, not the Markdown body heading. |
| `emoji` | None | Prefixes the navigation title. |
| `order` | `999` | Integer sort order; lower values appear first. Invalid integers retain `999`. |
| `description` | None | Short description displayed above the rendered body. |
| `tags` | Empty list | Tag badges and sidebar search terms. |
| `draft` | `false` | Excludes the page when its value is `true`, `yes`, `1`, or `on`, case-insensitively. |

Fields are parsed as simple text values, not full YAML. Values may be unquoted
or wrapped in matching single or double quotes. Escape sequences and nested
objects are not interpreted. Keys are normalized to lowercase. Blank lines and
lines beginning with `#` in the metadata block are ignored. Unknown keys are
retained in `Frontmatter.extra` but do not affect generated output.

Tags accept an inline list or a block list:

```yaml
tags: [api, "getting started"]
```

```yaml
tags:
  - api
  - getting started
```

A single scalar tag is accepted. Inline commas inside matching quotes do not
split the tag.

## Section helpers

Place `_section.md` or `index.md` in a documentation directory to customize
the corresponding navigation section:

```text
docs/guides/
├── _section.md
├── deployment.md
└── troubleshooting.md
```

`title`, `emoji`, `order`, and `description` customize the section. `_section.md`
takes precedence over `index.md` when both exist. Both files are reserved and
are not emitted as pages. Only the body of `_section.md` becomes section landing
content; `index.md` contributes metadata but its body is ignored. A helper file
without frontmatter is treated as body text by the parser, but only
`_section.md` displays that body.
