---
title: HTML generation and browser runtime
order: 3
tags: [generator, browser]
---

# HTML generation and browser runtime

`generate_html(scan_result, output_path="docs.html", *, title=None,
theme="auto", primary_color="#2563eb")` in `emdg.generator` builds the
single-file site.

## Serialization and template assembly

The generator recursively serializes `DocItem` and `DocSection` data. For each
page, it reads the UTF-8 source file and strips frontmatter to get the Markdown
body. The payload includes the site title, a UTC generation timestamp, home
page, root pages, and nested sections.

The payload is encoded as JSON and assigned to `window.__DOCS__` in the HTML
template. The generator escapes `</` in serialized content so Markdown cannot
prematurely close the containing script element. It HTML-escapes the title for
use in HTML text/attributes, validates the theme and primary color, writes
UTF-8 output, and returns its resolved `Path`.

The output parent directory is not created automatically. Writing fails if it
does not exist. Invalid themes and primary colors raise `ValueError`. The
primary color must use `#RGB` or `#RRGGBB` syntax.

> [!NOTE]
> Markdown bodies are embedded in the generated file and rendered in the
> browser; generation does not produce a separate HTML page per document.

## Theme colors

The CLI accepts the primary accent with `--primary-color`; the API accepts it
as `primary_color`. The generator derives separate light and dark accent
variants from that hex color, adjusting the variants to maintain at least 4.5:1
contrast against their theme backgrounds. The dark theme uses neutral gray
backgrounds, borders, code surfaces, and tags instead of blue-tinted grays.

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

> [!CAUTION]
> Treat Markdown as trusted input before publishing. Raw HTML in a source page
> can run in the generated site's browser context.

Tailwind CSS, Marked, Highlight.js, and Mermaid are loaded from public CDNs.
Without network access, the source text remains embedded, but styling and
Markdown rendering may not work. The generator does not sanitize raw HTML in
Markdown before Marked renders it. Generate and publish sites only from trusted
documentation sources.
