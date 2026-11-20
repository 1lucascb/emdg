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


def _contrast_ratio(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))

    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


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
    assert ".empty-state" in html
    assert ".code-wrapper" in html
    assert "function enhanceCodeBlocks()" in html
    assert 'document.createElement("details")' in html
    assert 'document.createElement("summary")' in html
    assert "group.open = Boolean(q) || openSections.has(sec.slug)" in html
    assert 'let section = el.parentElement.closest("details.section-group")' in html
    assert "tagEl.textContent = `#${tag}`" in html
    assert "tagsEl.innerHTML" not in html
    payload = _payload(html)
    assert payload["root_items"][0]["body"] == "```mermaid\ngraph TD\n  A --> B\n```\n"
    assert payload["root_items"][0]["tags"] == ["flow"]


def test_markdown_file_links_are_resolved_against_embedded_source_paths(
    tmp_path: Path,
) -> None:
    (tmp_path / "guide" / "start.md").parent.mkdir()
    (tmp_path / "guide" / "start.md").write_text(
        'See [imports](../ref/imports.md#examples).\n', encoding="utf-8"
    )
    (tmp_path / "ref" / "imports.md").parent.mkdir()
    (tmp_path / "ref" / "imports.md").write_text("# Imports\n", encoding="utf-8")

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")
    payload = _payload(html)

    guide = payload["sections"][0]["items"][0]
    assert guide["path"] == "guide/start.md"
    assert payload["sections"][1]["items"][0]["path"] == "ref/imports.md"
    assert "function rewriteMarkdownLinks(page)" in html
    assert 'link.href = `#/${destination.slug}${fragment}`' in html


def test_root_readme_is_default_home_and_title_link_target(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Home page\n", encoding="utf-8")
    (tmp_path / "overview.md").write_text("# Overview\n", encoding="utf-8")

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")
    payload = _payload(html)

    assert payload["home"]["body"] == "# Home page\n"
    assert [item["title"] for item in payload["root_items"]] == ["Overview"]
    assert 'id="siteHome"' in html
    assert 'id="mobileSiteHome"' in html
    assert "if (homeSlug)" in html
    assert 'homeLink.href = `#/${homeSlug}`' in html
    assert 'mobileHomeLink.href = `#/${homeSlug}`' in html
    assert "pagesBySlug.set(tree.home.slug, tree.home)" in html
    assert "window.__DOCS__.home.slug" in html
    generated_at = datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))
    assert generated_at.utcoffset() == timezone.utc.utcoffset(generated_at)
    assert '<footer id="homeFooter"' in html
    assert "page.slug === window.__DOCS__.home.slug" in html
    assert ".slice(0, -5)" in html
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


def test_mobile_menu_stays_open_for_section_navigation_and_closes_for_pages(
    tmp_path: Path,
) -> None:
    (tmp_path / "guide" / "_section.md").parent.mkdir()
    (tmp_path / "guide" / "_section.md").write_text(
        "# Guide overview\n", encoding="utf-8"
    )
    (tmp_path / "guide" / "page.md").write_text("# Page\n", encoding="utf-8")

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")

    assert 'window.matchMedia("(max-width: 860px)")' in html
    assert "if (mobileViewport.matches) setMobileMenu(false)" in html
    assert "if (!wasOpen) group.open = true;" in html
    assert "setMobileMenu(false);\n            const targetHash" not in html


def test_generated_pages_include_local_toc_and_callout_rendering(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text(
        "# Guide\n\n## Setup\n\nDetails.\n\n## Setup\n\nMore details.\n\n"
        "> [!WARNING]\n> Be careful.\n",
        encoding="utf-8",
    )

    output = generate_html(scan_docs(tmp_path), tmp_path / "site.html")
    html = output.read_text(encoding="utf-8")
    body = _payload(html)["root_items"][0]["body"]

    assert "## Setup" in body
    assert "> [!WARNING]" in body
    assert 'id="tableOfContents"' in html
    assert "function renderTableOfContents(page)" in html
    assert "heading-${base}-${suffix++}" in html
    assert "function enhanceCallouts()" in html
    assert "callout-${type}" in html
    assert ".callout-warning" in html


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


def test_custom_primary_color_supports_neutral_light_and_dark_themes(
    tmp_path: Path,
) -> None:
    output = generate_html(
        scan_docs(tmp_path),
        tmp_path / "site.html",
        primary_color="#174ea6",
    )

    html = output.read_text(encoding="utf-8")
    accents = re.findall(r"--accent: (#[0-9a-f]{6});", html)
    assert accents[0] == "#174ea6"
    assert accents[1] != accents[0]
    assert "--bg: #09090b;" in html
    assert "--bg-sidebar: #111114;" in html
    assert "__PRIMARY_" not in html


def test_rejects_unknown_theme(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="theme"):
        generate_html(scan_docs(tmp_path), tmp_path / "site.html", theme="blue")


def test_rejects_invalid_primary_color(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="primary_color"):
        generate_html(scan_docs(tmp_path), tmp_path / "site.html", primary_color="blue")


@pytest.mark.parametrize("primary_color", ["#fff", "#000", "#f00", "#174ea6"])
def test_primary_color_accents_meet_contrast_threshold(
    tmp_path: Path, primary_color: str
) -> None:
    output = generate_html(
        scan_docs(tmp_path),
        tmp_path / "site.html",
        primary_color=primary_color,
    )
    html = output.read_text(encoding="utf-8")
    light = re.search(r":root \{(.*?)\}", html, re.DOTALL)
    dark = re.search(r'\[data-theme="dark"\] \{(.*?)\}', html, re.DOTALL)
    assert light and dark

    for theme in (light.group(1), dark.group(1)):
        accent = re.search(r"--accent: (#[0-9a-f]{6});", theme)
        soft = re.search(r"--accent-soft: (#[0-9a-f]{6});", theme)
        assert accent and soft
        assert _contrast_ratio(accent.group(1), soft.group(1)) >= 4.5


def test_escapes_title_in_html_attributes(tmp_path: Path) -> None:
    output = generate_html(
        scan_docs(tmp_path),
        tmp_path / "site.html",
        title='Docs "onclick="alert(1)',
    )

    html = output.read_text(encoding="utf-8")
    assert 'aria-label="Docs &quot;onclick=&quot;alert(1) home"' in html
