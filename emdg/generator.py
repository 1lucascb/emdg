from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from emdg.frontmatter import parse_frontmatter
from emdg.scanner import DocItem, DocSection, ScanResult, humanize_name

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__SITE_TITLE__</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {
      --bg: #ffffff;
      --bg-sidebar: #f8fafc;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --accent: #2563eb;
      --accent-soft: #eff6ff;
      --code-bg: #1e293b;
      --tag-bg: #e2e8f0;
      --callout-tip: #059669;
      --callout-important: #7c3aed;
      --callout-warning: #d97706;
      --callout-caution: #dc2626;
      color-scheme: light;
    }
    [data-theme="dark"] {
      --bg: #0b1120;
      --bg-sidebar: #0f172a;
      --border: #1e293b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #60a5fa;
      --accent-soft: #1e293b;
      --code-bg: #020617;
      --tag-bg: #1e293b;
      --callout-tip: #34d399;
      --callout-important: #c4b5fd;
      --callout-warning: #fbbf24;
      --callout-caution: #f87171;
      color-scheme: dark;
    }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      transition: background-color 160ms ease, color 160ms ease;
    }
    .app-sidebar {
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border);
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
    }
    .app-header { color: var(--text-muted); }
    .app-header .current { color: var(--text); }
    .theme-btn {
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      cursor: pointer;
      transition: background-color 160ms ease, border-color 160ms ease;
    }
    .theme-btn:hover {
      background: var(--accent-soft);
      border-color: var(--accent);
    }
    #search {
      width: 100%;
      padding: 0.65rem 0.75rem;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      outline: none;
      transition: border-color 160ms ease, box-shadow 160ms ease;
    }
    #search:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
    }
    .section-group { display: block; }
    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin: 0.35rem 0;
      padding: 0.55rem 0.65rem;
      border-radius: 0.6rem;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }
    .section-title::-webkit-details-marker { display: none; }
    .section-title:hover { background: var(--accent-soft); color: var(--text); }
    .section-title.active { background: var(--accent-soft); color: var(--accent); }
    .section-chevron { flex: 0 0 auto; transition: transform 140ms ease; }
    .section-group[open] > .section-title .section-chevron { transform: rotate(90deg); }
    .section-content { display: flex; flex-direction: column; gap: 0.2rem; }
    .subsection {
      padding-left: 0.65rem;
      border-left: 1px solid var(--border);
      margin: 0.25rem 0 0.25rem 0.65rem;
    }
    .nav-link {
      display: block;
      padding: 0.5rem 0.7rem;
      border-radius: 0.6rem;
      color: var(--text);
      text-decoration: none;
      font-size: 0.9rem;
      transition: background-color 140ms ease, color 140ms ease;
    }
    .nav-link:hover { background: var(--accent-soft); }
    .nav-link.active {
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 600;
    }
    .app-main {
      width: 100%;
      min-width: 0;
      padding: 2.5rem clamp(1.25rem, 5vw, 4.5rem);
    }
    .doc-meta {
      margin: 0 auto 2rem;
      max-width: 62.4rem;
      padding: 1.25rem 1.5rem;
      border: 1px solid var(--border);
      border-radius: 1rem;
      background: var(--bg-sidebar);
    }
    .toc {
      max-width: 62.4rem;
      margin: 0 auto 2rem;
      padding: 1rem 1.25rem;
      border: 1px solid var(--border);
      border-radius: 0.85rem;
      background: var(--bg-sidebar);
    }
    .toc-title {
      margin: 0;
      color: var(--text-muted);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    #tocLinks { margin: 0.5rem 0 0; padding-left: 1.25rem; }
    #tocLinks li { margin: 0.25rem 0; }
    #tocLinks .toc-level-3 { margin-left: 1rem; }
    #tocLinks a { color: var(--accent); text-decoration: none; }
    #tocLinks a:hover { text-decoration: underline; }
    .home-footer {
      max-width: 62.4rem;
      margin: 3rem auto 0;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
    }
    .doc-desc { color: var(--text-muted); margin: 0 0 0.75rem; }
    .tags { display: flex; gap: 0.45rem; flex-wrap: wrap; }
    .tag {
      font-size: 0.75rem;
      background: var(--tag-bg);
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      color: var(--text-muted);
    }
    #content {
      max-width: 62.4rem;
      margin: 0 auto;
      line-height: 1.65;
    }
    .empty-state {
      border: 1px solid var(--border);
      border-radius: 1rem;
      background: var(--bg-sidebar);
      padding: 2rem;
    }
    #content h1, #content h2, #content h3, #content h4 {
      color: var(--text);
      font-weight: 700;
      line-height: 1.25;
      scroll-margin-top: 2rem;
    }
    #content h1 { font-size: clamp(2rem, 4vw, 2.75rem); letter-spacing: -0.04em; }
    #content h2 {
      margin-top: 2.5rem;
      padding-bottom: 0.55rem;
      border-bottom: 1px solid var(--border);
      font-size: 1.6rem;
      letter-spacing: -0.025em;
    }
    #content h3 { margin-top: 2rem; font-size: 1.25rem; }
    #content p, #content ul, #content ol { margin: 1rem 0; }
    #content ul, #content ol { padding-left: 1.5rem; }
    #content ul { list-style: disc; }
    #content ol { list-style: decimal; }
    #content li { padding-left: 0.25rem; margin: 0.35rem 0; }
    #content a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }
    #content img { max-width: 100%; height: auto; border-radius: 0.75rem; }
    #content hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
    #content pre {
      margin: 1.25rem 0;
      background: var(--code-bg);
      padding: 1.1rem 1.25rem;
      border: 1px solid var(--border);
      border-radius: 0.85rem;
      overflow-x: auto;
    }
    #content pre code { background: transparent; padding: 0; }
    #content code {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.875em;
    }
    #content :not(pre) > code {
      background: var(--tag-bg);
      padding: 0.15rem 0.4rem;
      border-radius: 0.35rem;
    }
    #content table {
      display: block;
      max-width: 100%;
      overflow-x: auto;
      border-collapse: collapse;
      margin: 1.25rem 0;
    }
    #content th, #content td {
      border: 1px solid var(--border);
      padding: 0.65rem 0.85rem;
      text-align: left;
    }
    #content th { background: var(--bg-sidebar); font-weight: 600; }
    #content blockquote {
      margin: 1.25rem 0;
      padding: 0.8rem 1rem;
      border-left: 3px solid var(--accent);
      border-radius: 0 0.65rem 0.65rem 0;
      background: var(--accent-soft);
    }
    #content blockquote.callout {
      border-left-color: var(--callout-color);
      background: color-mix(in srgb, var(--callout-color) 9%, var(--bg));
    }
    #content .callout-note { --callout-color: var(--accent); }
    #content .callout-tip { --callout-color: var(--callout-tip); }
    #content .callout-important { --callout-color: var(--callout-important); }
    #content .callout-warning { --callout-color: var(--callout-warning); }
    #content .callout-caution { --callout-color: var(--callout-caution); }
    #content .callout-title {
      margin: 0 0 0.35rem;
      color: var(--callout-color);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .mermaid {
      display: flex;
      justify-content: center;
      margin: 1.5rem 0;
      padding: 1rem;
      border: 1px solid var(--border);
      border-radius: 0.85rem;
      background: var(--bg-sidebar);
    }
    @media (max-width: 768px) {
      .app-sidebar { width: 100%; height: auto; position: static; border-right: 0; border-bottom: 1px solid var(--border); }
      .app-main { padding-top: 1.75rem; }
    }
  </style>
</head>
<body class="flex min-h-screen antialiased">
  <aside class="app-sidebar flex w-72 shrink-0 flex-col gap-6 px-5 py-6">
    <div class="flex items-center justify-between gap-3">
      <a class="flex min-w-0 items-center text-inherit no-underline" href="#/" id="siteHome" aria-label="__SITE_TITLE__ home">
        <span class="truncate text-sm font-semibold tracking-tight">__SITE_TITLE__</span>
      </a>
      <button class="theme-btn rounded-lg px-2.5 py-2 text-xs font-medium" id="themeToggle" title="Toggle theme" aria-label="Toggle theme">Theme</button>
    </div>
    <div>
      <p class="mb-2 px-1 text-xs font-semibold uppercase tracking-widest text-slate-400">Documentation</p>
      <label class="sr-only" for="search">Search documentation</label>
      <input class="rounded-xl text-sm" id="search" type="search" placeholder="Search pages..." autocomplete="off" />
    </div>
    <nav class="flex flex-col gap-2" id="sidebarNav" aria-label="Documentation navigation"></nav>
  </aside>

  <main class="app-main">
    <header class="app-header mx-auto mb-9 flex max-w-4xl items-center gap-2 text-sm">
      <span>Docs</span><span aria-hidden="true">/</span><span class="current font-medium" id="siteTitle">__SITE_TITLE__</span>
    </header>
    <div id="docMeta" class="doc-meta" hidden>
      <p id="docDesc" class="doc-desc"></p>
      <div id="docTags" class="tags"></div>
    </div>
    <nav id="tableOfContents" class="toc" aria-label="On this page" hidden>
      <p class="toc-title">On this page</p>
      <ol id="tocLinks"></ol>
    </nav>
    <article id="content"></article>
    <footer id="homeFooter" class="home-footer" hidden>
      Last updated at: <time id="lastUpdated"></time>
    </footer>
  </main>

  <script>
    window.__DOCS__ = __DOCS_JSON__;

    const formatLabel = (entry) => entry.emoji ? `${entry.emoji} ${entry.title}` : entry.title;

    const pagesBySlug = new Map();
    const sectionsBySlug = new Map();
    function indexPages(tree) {
      if (tree.home) pagesBySlug.set(tree.home.slug, tree.home);
      for (const item of tree.root_items) pagesBySlug.set(item.slug, item);
      function walk(sections) {
        for (const sec of sections) {
          if (sec.body && sec.body.trim()) sectionsBySlug.set(sec.slug, sec);
          for (const item of sec.items) pagesBySlug.set(item.slug, item);
          walk(sec.subsections);
        }
      }
      walk(tree.sections);
    }
    indexPages(window.__DOCS__);
    const homeLink = document.getElementById("siteHome");
    const homeSlug = window.__DOCS__.home
      ? window.__DOCS__.home.slug
      : pagesBySlug.keys().next().value;
    if (homeSlug) homeLink.href = `#/${homeSlug}`;

    const navEl = document.getElementById("sidebarNav");
    const contentEl = document.getElementById("content");
    const metaEl = document.getElementById("docMeta");
    const descEl = document.getElementById("docDesc");
    const tagsEl = document.getElementById("docTags");
    const homeFooterEl = document.getElementById("homeFooter");
    const lastUpdatedEl = document.getElementById("lastUpdated");
    const tocEl = document.getElementById("tableOfContents");
    const tocLinksEl = document.getElementById("tocLinks");
    const searchEl = document.getElementById("search");
    const openSections = new Set();

    function routeSlugFromHash() {
      return decodeURIComponent(location.hash.replace(/^#\\/?/, "").split("#", 1)[0]);
    }

    function headingIdFromHash() {
      const parts = location.hash.split("#");
      return parts.length > 2 ? decodeURIComponent(parts.slice(2).join("#")) : "";
    }

    function renderTableOfContents(page) {
      const headings = [...contentEl.querySelectorAll("h2, h3")];
      const usedIds = new Set();
      tocLinksEl.replaceChildren();

      headings.forEach((heading, index) => {
        const base = heading.textContent
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9 -]/g, "")
          .replace(/ +/g, "-")
          .replace(/-+/g, "-") || `section-${index + 1}`;
        let id = `heading-${base}`;
        let suffix = 2;
        while (usedIds.has(id)) id = `heading-${base}-${suffix++}`;
        usedIds.add(id);
        heading.id = id;

        const item = document.createElement("li");
        if (heading.tagName === "H3") item.className = "toc-level-3";
        const link = document.createElement("a");
        link.href = `#/${page.slug}#${encodeURIComponent(id)}`;
        link.textContent = heading.textContent;
        item.appendChild(link);
        tocLinksEl.appendChild(item);
      });

      tocEl.hidden = headings.length === 0;
    }

    function enhanceCallouts() {
      const types = new Set(["NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"]);
      contentEl.querySelectorAll("blockquote").forEach((quote) => {
        const paragraph = quote.querySelector("p");
        const marker = paragraph &&
          paragraph.textContent.match(/^\\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\\]/i);
        if (!marker || !types.has(marker[1].toUpperCase())) return;

        const type = marker[1].toLowerCase();
        quote.classList.add("callout", `callout-${type}`);
        const label = document.createElement("div");
        label.className = "callout-title";
        label.textContent = type;
        quote.prepend(label);

        let charactersToRemove = marker[0].length;
        const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT);
        let textNode = walker.nextNode();
        while (textNode && charactersToRemove > 0) {
          const count = Math.min(charactersToRemove, textNode.textContent.length);
          textNode.textContent = textNode.textContent.slice(count);
          charactersToRemove -= count;
          textNode = walker.nextNode();
        }
        if (!paragraph.textContent.trim()) paragraph.remove();
      });
    }

    function renderSidebar(filter = "") {
      const q = filter.trim().toLowerCase();
      navEl.innerHTML = "";

      const makeLink = (item) => {
        const a = document.createElement("a");
        a.href = `#/${item.slug}`;
        a.className = "nav-link";
        a.dataset.slug = item.slug;
        a.textContent = formatLabel(item);
        return a;
      };

      const matches = (item) =>
        !q ||
        item.title.toLowerCase().includes(q) ||
        item.body.toLowerCase().includes(q) ||
        (item.tags || []).some((t) => t.toLowerCase().includes(q));

      for (const item of window.__DOCS__.root_items) {
        if (matches(item)) navEl.appendChild(makeLink(item));
      }

      
      function buildSection(sec, isSub = false) {
        const group = document.createElement("details");
        group.className = isSub ? "section-group subsection" : "section-group";
        group.dataset.sectionSlug = sec.slug;

        const matchingItems = sec.items.filter(matches);
        const subNodes = sec.subsections
          .map((sub) => buildSection(sub, true))
          .filter(Boolean);

        if (matchingItems.length === 0 && subNodes.length === 0) return null;

        group.open = Boolean(q) || openSections.has(sec.slug);
        group.addEventListener("toggle", () => {
          if (searchEl.value.trim()) return;
          if (group.open) openSections.add(sec.slug);
          else openSections.delete(sec.slug);
        });

        const heading = document.createElement("summary");
        heading.className = "section-title";
        heading.dataset.sectionSlug = sec.slug;
        const label = document.createElement("span");
        label.textContent = formatLabel(sec);
        const chevron = document.createElement("span");
        chevron.className = "section-chevron";
        chevron.setAttribute("aria-hidden", "true");
        chevron.innerHTML = "&#8250;";
        heading.append(label, chevron);
        heading.addEventListener("click", () => {
          if (!sec.body || !sec.body.trim()) return;
          const wasOpen = group.open;
          setTimeout(() => {
            if (!wasOpen) group.open = true;
            const targetHash = `#/${sec.slug}`;
            if (location.hash === targetHash) renderPage(sec.slug);
            else location.hash = `/${sec.slug}`;
          }, 0);
        });
        group.appendChild(heading);

        const content = document.createElement("div");
        content.className = "section-content";
        for (const item of matchingItems) content.appendChild(makeLink(item));
        for (const subNode of subNodes) content.appendChild(subNode);
        group.appendChild(content);
        return group;
      }

      for (const sec of window.__DOCS__.sections) {
        const node = buildSection(sec, false);
        if (node) navEl.appendChild(node);
      }

      highlightActiveLink();
    }

    function highlightActiveLink() {
      const currentSlug = routeSlugFromHash();
      document.querySelectorAll(".nav-link").forEach((el) => {
        el.classList.toggle("active", el.dataset.slug === currentSlug);
        if (el.dataset.slug !== currentSlug) return;
        let section = el.parentElement.closest("details.section-group");
        while (section) {
          section.open = true;
          openSections.add(section.dataset.sectionSlug);
          section = section.parentElement.closest("details.section-group");
        }
      });
      document.querySelectorAll(".section-title[data-section-slug]").forEach((el) => {
        el.classList.toggle("active", el.dataset.sectionSlug === currentSlug);
      });
    }

    async function renderPage(slug) {
      homeFooterEl.hidden = true;
      const firstSlug = window.__DOCS__.home
        ? window.__DOCS__.home.slug
        : pagesBySlug.keys().next().value;
      const page = pagesBySlug.get(slug) || sectionsBySlug.get(slug) || pagesBySlug.get(firstSlug);

      if (!page) {
        tocEl.hidden = true;
        contentEl.innerHTML = '<div class="empty-state"><h1>No Markdown files found</h1><p>Add some .md files and rebuild to get started.</p></div>';
        return;
      }

      if (routeSlugFromHash() !== page.slug) {
        history.replaceState(null, "", `#/${page.slug}`);
      }

      if (window.__DOCS__.home && page.slug === window.__DOCS__.home.slug) {
        const generatedAt = window.__DOCS__.generated_at;
        homeFooterEl.hidden = false;
        lastUpdatedEl.dateTime = generatedAt;
        lastUpdatedEl.textContent = new Date(generatedAt)
          .toISOString()
          .slice(0, -5)
          .replace("T", " ")
          + " UTC";
      }

      if (page.description || (page.tags && page.tags.length)) {
        metaEl.hidden = false;
        descEl.textContent = page.description || "";
        descEl.hidden = !page.description;
        tagsEl.replaceChildren();
        for (const tag of page.tags || []) {
          const tagEl = document.createElement("span");
          tagEl.className = "tag";
          tagEl.textContent = `#${tag}`;
          tagsEl.appendChild(tagEl);
        }
      } else {
        metaEl.hidden = true;
      }

      contentEl.innerHTML = marked.parse(page.body);
      renderTableOfContents(page);
      enhanceCallouts();

      // Convert ```mermaid code blocks into <div class="mermaid">
      contentEl.querySelectorAll("pre code.language-mermaid").forEach((codeBlock) => {
        const div = document.createElement("div");
        div.className = "mermaid";
        div.textContent = codeBlock.textContent;
        codeBlock.parentElement.replaceWith(div);
      });

      // Highlight normal code blocks
      contentEl.querySelectorAll("pre code").forEach((block) => {
        hljs.highlightElement(block);
      });

      // Render Mermaid diagrams
      if (contentEl.querySelector(".mermaid")) {
        await mermaid.run({ querySelector: ".mermaid" });
      }

      highlightActiveLink();
      const heading = document.getElementById(headingIdFromHash());
      if (heading && contentEl.contains(heading)) heading.scrollIntoView();
      else window.scrollTo(0, 0);
    }

    // Theme handling
    const initialTheme = "__INITIAL_THEME__";
    const savedTheme = localStorage.getItem("emdg-theme") ||
      (initialTheme === "auto"
        ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
        : initialTheme);
    document.documentElement.dataset.theme = savedTheme;

    document.getElementById("themeToggle").addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("emdg-theme", next);
    });

    mermaid.initialize({ startOnLoad: false, theme: "default" });
    searchEl.addEventListener("input", (e) => renderSidebar(e.target.value));
    window.addEventListener("hashchange", () => {
      renderPage(routeSlugFromHash());
    });

    renderSidebar();
    renderPage(routeSlugFromHash());
  </script>
</body>
</html>
"""

def _serialize_item(item: DocItem) -> dict:
    raw = item.path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(raw)
    return {
        "title": item.title,
        "emoji": item.emoji,
        "slug": item.slug,
        "order": item.order,
        "description": item.description,
        "tags": item.tags,
        "body": body,
    }


def _serialize_section(section: DocSection) -> dict:
    return {
        "title": section.title,
        "emoji": section.emoji,
        "slug": section.slug,
        "order": section.order,
        "description": section.description,
        "body": section.body,
        "items": [_serialize_item(i) for i in section.items],
        "subsections": [_serialize_section(s) for s in section.subsections],
    }


def generate_html(
    scan_result: ScanResult,
    output_path: str | Path = "docs.html",
    *,
    title: str | None = None,
    theme: str = "auto",
) -> Path:
    """Build a single-file HTML documentation page from a ScanResult."""
    if theme not in {"auto", "light", "dark"}:
        raise ValueError("theme must be 'auto', 'light', or 'dark'")

    site_title = title or humanize_name(scan_result.root.name)

    payload = {
        "title": site_title,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "home": _serialize_item(scan_result.home) if scan_result.home else None,
        "root_items": [_serialize_item(i) for i in scan_result.root_items],
        "sections": [_serialize_section(s) for s in scan_result.sections],
    }

    # Escape '</script>' inside Markdown content so it cannot prematurely close the script tag
    safe_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    replacements = {
        "__SITE_TITLE__": html.escape(site_title, quote=True),
        "__DOCS_JSON__": safe_json,
        "__INITIAL_THEME__": theme,
    }
    final_html = re.sub(
        r"__SITE_TITLE__|__DOCS_JSON__|__INITIAL_THEME__",
        lambda match: replacements[match.group(0)],
        HTML_TEMPLATE,
    )

    out = Path(output_path).resolve()
    out.write_text(final_html, encoding="utf-8")
    return out