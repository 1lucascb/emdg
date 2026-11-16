from pathlib import Path

import pytest

from emdg.scanner import scan_docs


def _write(path: Path, content: str = "# Body\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_scans_and_sorts_root_items_sections_and_nested_sections(tmp_path: Path) -> None:
    _write(tmp_path / "zebra.md")
    _write(tmp_path / "alpha.md", "---\norder: 1\n---\nAlpha\n")
    _write(tmp_path / "how-it-works" / "pagination.md")
    _write(tmp_path / "how-it-works" / "deep-guide" / "setup.md")
    _write(tmp_path / "zebra-section" / "page.md")
    _write(tmp_path / "alpha-section" / "page.md")
    _write(
        tmp_path / "priority-section" / "_section.md",
        "---\ntitle: Priority\norder: 1\n---\n",
    )
    _write(tmp_path / "priority-section" / "page.md")

    result = scan_docs(tmp_path)

    assert [item.title for item in result.root_items] == ["Alpha", "Zebra"]
    assert [section.title for section in result.sections] == [
        "Priority",
        "Alpha Section",
        "How It Works",
        "Zebra Section",
    ]
    section = result.sections[2]
    assert section.title == "How It Works"
    assert [item.title for item in section.items] == ["Pagination"]
    assert section.subsections[0].title == "Deep Guide"
    assert section.subsections[0].items[0].slug == "how-it-works/deep-guide/setup"


def test_root_readme_is_home_and_not_a_sidebar_item(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "# Welcome\n")
    _write(tmp_path / "overview.md", "# Overview\n")
    _write(tmp_path / "guide" / "README.md", "# Guide readme\n")

    result = scan_docs(tmp_path)

    assert result.home is not None
    assert result.home.relative_path == Path("README.md")
    assert result.home.slug == "README"
    assert [item.title for item in result.root_items] == ["Overview"]
    assert [item.title for item in result.sections[0].items] == ["Readme"]


def test_frontmatter_customizes_item_and_section_and_hides_helpers(tmp_path: Path) -> None:
    _write(
        tmp_path / "api" / "_section.md",
        "---\ntitle: API Reference\nemoji: 🔌\norder: 2\ndescription: Endpoints\n---\n"
        "# API Reference\nSection content.\n",
    )
    _write(tmp_path / "api" / "index.md", "---\ntitle: Index\n---\n")
    _write(
        tmp_path / "api" / "page.md",
        "---\ntitle: Custom Page\nemoji: 📄\ntags: [api, guide]\n---\nContent\n",
    )

    result = scan_docs(tmp_path)

    section = result.sections[0]
    assert (section.title, section.emoji, section.order, section.description) == (
        "API Reference",
        "🔌",
        2,
        "Endpoints",
    )
    assert section.body == "# API Reference\nSection content.\n"
    assert len(section.items) == 1
    assert section.items[0].title == "Custom Page"
    assert section.items[0].emoji == "📄"
    assert section.items[0].tags == ["api", "guide"]


def test_index_metadata_is_used_when_section_file_is_absent(tmp_path: Path) -> None:
    _write(tmp_path / "guide" / "index.md", "---\ntitle: User Guide\n---\nIgnored body\n")
    _write(tmp_path / "guide" / "intro.md")

    result = scan_docs(tmp_path)

    assert result.sections[0].title == "User Guide"
    assert result.sections[0].body == ""
    assert [item.title for item in result.sections[0].items] == ["Intro"]


def test_ignores_default_dot_and_custom_entries_and_prunes_empty_sections(
    tmp_path: Path,
) -> None:
    _write(tmp_path / ".hidden" / "hidden.md")
    _write(tmp_path / "node_modules" / "ignored.md")
    _write(tmp_path / "private" / "secret.md")
    _write(tmp_path / "empty" / "notes.txt")
    _write(tmp_path / "visible.md")

    result = scan_docs(tmp_path, ignore={"private"})

    assert [item.title for item in result.root_items] == ["Visible"]
    assert result.sections == []


def test_draft_documents_and_sections_without_published_pages_are_pruned(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "draft.md", "---\ndraft: true\n---\n")
    _write(tmp_path / "drafts" / "only.md", "---\ndraft: true\n---\n")
    _write(tmp_path / "published" / "page.md")

    result = scan_docs(tmp_path)

    assert [item.title for item in result.root_items] == []
    assert [section.title for section in result.sections] == ["Published"]


def test_raises_for_missing_or_non_directory_origin(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_docs(tmp_path / "missing")

    file_path = _write(tmp_path / "file.md")
    with pytest.raises(NotADirectoryError):
        scan_docs(file_path)
