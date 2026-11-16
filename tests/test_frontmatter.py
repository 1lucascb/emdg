from emdg.frontmatter import Frontmatter, parse_frontmatter


def test_plain_markdown_is_unchanged() -> None:
    content = "# Hello\n\nBody\n"

    metadata, body = parse_frontmatter(content)

    assert metadata == Frontmatter()
    assert body == content


def test_parses_all_fields_and_inline_tags() -> None:
    metadata, body = parse_frontmatter(
        "---\n"
        "title: Cursor Pagination\n"
        "emoji: 📄\n"
        "order: 1\n"
        "description: How cursors work\n"
        "draft: true\n"
        'tags: [api, "page, size"]\n'
        "custom: value\n"
        "---\n"
        "\n# Content\n"
    )

    assert metadata.title == "Cursor Pagination"
    assert metadata.emoji == "📄"
    assert metadata.order == 1
    assert metadata.description == "How cursors work"
    assert metadata.draft is True
    assert metadata.tags == ["api", "page, size"]
    assert metadata.extra == {"custom": "value"}
    assert body == "# Content\n"


def test_parses_quoted_values_block_tags_and_invalid_order() -> None:
    metadata, _ = parse_frontmatter(
        "---\n"
        "title: 'Single quoted'\n"
        'description: "Double quoted"\n'
        "order: later\n"
        "tags:\n"
        "  - first\n"
        "  - 'second tag'\n"
        "---\n"
        "Body"
    )

    assert metadata.title == "Single quoted"
    assert metadata.description == "Double quoted"
    assert metadata.order == 999
    assert metadata.tags == ["first", "second tag"]


def test_unclosed_frontmatter_is_left_as_body() -> None:
    content = "---\ntitle: Missing close\n# body"

    metadata, body = parse_frontmatter(content)

    assert metadata == Frontmatter()
    assert body == content


def test_body_delimiter_inside_code_fence_is_preserved() -> None:
    content = "---\ntitle: Example\n---\n```text\n---\n```\n"

    metadata, body = parse_frontmatter(content)

    assert metadata.title == "Example"
    assert body == "```text\n---\n```\n"
