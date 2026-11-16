---
title: Architecture
order: 1
description: Package boundaries and the path from source Markdown to a browser-rendered site.
---

The implementation has a small build-time pipeline and a self-contained
client-side application. The Python side discovers files, extracts metadata,
builds a typed tree, and serializes that tree. The browser side routes between
the embedded pages and renders their Markdown.
