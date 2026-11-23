---
title: Callout markers
order: 4
description: Supported blockquote markers and how they appear in generated pages.
---

# Callout markers

`emdg` recognizes GitHub-style markers at the start of a blockquote's first
paragraph and renders the quote as a styled callout. Marker names are
case-insensitive. The generated callout heading shows the matching icon beside
the marker name in uppercase.

| Marker | Heading |
| --- | --- |
| `NOTE` | ℹ️ NOTE |
| `TIP` | 💡 TIP |
| `IMPORTANT` | ❗ IMPORTANT |
| `WARNING` | ⚠️ WARNING |
| `CAUTION` | ⛔ CAUTION |

Write the marker on its own line, followed by the callout content:

```markdown
> [!NOTE]
> This adds context for the reader.

> [!WARNING]
> Check this before continuing.
```

The marker may also be followed by text in the same paragraph. The marker is
removed from the displayed body, while the remaining text appears under the
icon and name. Blockquotes without a supported marker keep their normal
blockquote styling.

## Preview

These examples use actual markers, so they render as callouts in the generated
documentation:

> [!NOTE]
> This is a note callout.

> [!TIP]
> This is a tip callout.

> [!IMPORTANT]
> This is an important callout.

> [!WARNING]
> This is a warning callout.

> [!CAUTION]
> This is a caution callout.
