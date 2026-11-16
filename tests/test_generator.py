import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from emdg.generator import generate_html
from emdg.scanner import scan_docs


def _payload(html: str) -> dict:
    match = re.search(r"window\.__DOCS__ = (.*?);\s*const formatLabel", html, re.DOTALL)
    assert match
    return json.loads(match.group(1))


def test_generates_html_payload_with_markdown_and_mermaid(tmp_path: Path) -> None:
    (tmp_path / "diagram.md").write_text(
        "---\ntitle: Diagram\ntags: [flow]\n---\n"
        "```mermaid\ngraph TD\n  A --> B\n```\n",
        encoding="utf-8",
    )

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")

    assert output == (tmp_path / "site.html").resolve()
    html = output.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "window.__DOCS__" in html
    assert '<script src="https://cdn.tailwindcss.com"></script>' in html
    assert 'class="app-sidebar flex w-72' in html
    assert "brand-mark" not in html
    assert "<svg" not in html
    assert ".empty-state" in html
    assert 'document.createElement("details")' in html
    assert 'document.createElement("summary")' in html
    assert "group.open = Boolean(q) || openSections.has(sec.slug)" in html
    assert 'let section = el.parentElement.closest("details.section-group")' in html
    assert "tagEl.textContent = `#${tag}`" in html
    assert "tagsEl.innerHTML" not in html
    payload = _payload(html)
    assert payload["root_items"][0]["body"] == "```mermaid\ngraph TD\n  A --> B\n```\n"
    assert payload["root_items"][0]["tags"] == ["flow"]


def test_root_readme_is_default_home_and_title_link_target(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Home page\n", encoding="utf-8")
    (tmp_path / "overview.md").write_text("# Overview\n", encoding="utf-8")

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")
    payload = _payload(html)

    assert payload["home"]["body"] == "# Home page\n"
    assert [item["title"] for item in payload["root_items"]] == ["Overview"]
    assert 'id="siteHome"' in html
    assert "if (homeSlug) homeLink.href = `#/${homeSlug}`" in html
    assert "pagesBySlug.set(tree.home.slug, tree.home)" in html
    assert "window.__DOCS__.home.slug" in html
    generated_at = datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))
    assert generated_at.utcoffset() == timezone.utc.utcoffset(generated_at)
    assert '<footer id="homeFooter"' in html
    assert "page.slug === window.__DOCS__.home.slug" in html
    assert '.slice(0, -5)' in html
    assert '+ " UTC"' in html


def test_section_helper_body_is_available_on_section_route(tmp_path: Path) -> None:
    (tmp_path / "guide" / "_section.md").parent.mkdir(parents=True)
    (tmp_path / "guide" / "_section.md").write_text(
        "---\ntitle: Guide\n---\n# Guide overview\nSection intro.\n",
        encoding="utf-8",
    )
    (tmp_path / "guide" / "page.md").write_text("# Page\n", encoding="utf-8")

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")
    section = _payload(html)["sections"][0]

    assert section["body"] == "# Guide overview\nSection intro.\n"
    assert "sectionsBySlug.set(sec.slug, sec)" in html
    assert "sectionsBySlug.get(slug)" in html
    assert "if (!sec.body || !sec.body.trim()) return" in html


def test_escapes_script_closers_in_embedded_markdown(tmp_path: Path) -> None:
    (tmp_path / "injection.md").write_text(
        "Before </script><script>alert(1)</script> after\n"
        "__SITE_TITLE__ __DOCS_JSON__ __INITIAL_THEME__\n",
        encoding="utf-8",
    )

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")

    assert "</script><script>alert(1)</script>" not in html
    assert (
        _payload(html)["root_items"][0]["body"]
        == "Before </script><script>alert(1)</script> after\n"
        "__SITE_TITLE__ __DOCS_JSON__ __INITIAL_THEME__\n"
    )


def test_empty_directory_and_theme_override(tmp_path: Path) -> None:
    output = generate_html(
        scan_docs(tmp_path), tmp_path / "site.html", title="Custom Docs", theme="dark"
    )

    html = output.read_text(encoding="utf-8")
    assert "<title>Custom Docs</title>" in html
    assert 'const initialTheme = "dark"' in html
    assert "No Markdown files found" in html
    assert _payload(html)["root_items"] == []


def test_rejects_unknown_theme(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="theme"):
        generate_html(scan_docs(tmp_path), tmp_path / "site.html", theme="blue")


def test_escapes_title_in_html_attributes(tmp_path: Path) -> None:
    output = generate_html(
        scan_docs(tmp_path),
        tmp_path / "site.html",
        title='Docs "onclick="alert(1)',
    )

    html = output.read_text(encoding="utf-8")
    assert 'aria-label="Docs &quot;onclick=&quot;alert(1) home"' in html
