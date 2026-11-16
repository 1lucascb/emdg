---
title: HTML generation and browser runtime
order: 3
tags: [generator, browser]
---

# HTML generation and browser runtime

`generate_html(scan_result, output_path="docs.html", *, title=None,
theme="auto")` in `emdg.generator` builds the single-file site.

## Serialization and template assembly

The generator recursively serializes `DocItem` and `DocSection` data. For each
page, it reads the UTF-8 source file and strips frontmatter to get the Markdown
body. The payload includes the site title, a UTC generation timestamp, home
page, root pages, and nested sections.

The payload is encoded as JSON and assigned to `window.__DOCS__` in the HTML
template. The generator escapes `</` in serialized content so Markdown cannot
prematurely close the containing script element. It HTML-escapes the title for
use in HTML text/attributes, validates that the theme is `auto`, `light`, or
`dark`, writes UTF-8 output, and returns its resolved `Path`.

The output parent directory is not created automatically. Writing fails if it
does not exist. Invalid themes raise `ValueError`.

## Browser routing and page rendering

The client indexes pages by their generated slugs and navigates using URL
hashes such as `#/guides/first-steps`. A section can be selected as a landing
route only when it has a nonempty `_section.md` body. The root README is the
initial home page when present; otherwise the first available page is used.
The site title links to that home route (or first page).

On route changes, the browser:

1. Parses the Markdown body with Marked.
2. Adds a table of contents for `##` and `###` headings, assigning unique
   heading IDs and preserving the page route in anchor hashes.
3. Converts supported `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and
   `[!CAUTION]` blockquote markers into styled callouts.
4. Converts Mermaid code blocks to diagram containers, highlights code with
   Highlight.js, and renders diagrams with Mermaid.
5. Displays page descriptions and tag badges when present.

The searchable sidebar matches page title, Markdown body, and tags. Sections
collapse and expand; the section containing the active page opens automatically.
The selected light/dark theme is saved in browser `localStorage` under
`emdg-theme`. The generated timestamp is displayed on the home page.

## Dependencies and trust boundary

Tailwind CSS, Marked, Highlight.js, and Mermaid are loaded from public CDNs.
Without network access, the source text remains embedded, but styling and
Markdown rendering may not work. The generator does not sanitize raw HTML in
Markdown before Marked renders it. Generate and publish sites only from trusted
documentation sources.
