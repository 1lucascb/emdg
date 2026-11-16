from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Frontmatter:
    title: str | None = None
    emoji: str | None = None
    order: int = 999
    description: str | None = None
    draft: bool = False
    tags: list[str] = field(default_factory=list)
    extra: dict[str, str] = field(default_factory=dict)

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "on"}


def _parse_tags(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts: list[str] = []
        current: list[str] = []
        quote: str | None = None
        for char in inner:
            if char in {"'", '"'}:
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
            if char == "," and quote is None:
                part = "".join(current).strip()
                if part:
                    parts.append(_strip_quotes(part))
                current = []
            else:
                current.append(char)
        part = "".join(current).strip()
        if part:
            parts.append(_strip_quotes(part))
        return parts
    return [_strip_quotes(raw)] if raw else []


def parse_frontmatter(content: str) -> tuple[Frontmatter, str]:
    """
    Extract YAML-like frontmatter from Markdown content.

    Returns (Frontmatter, body_without_frontmatter).
    """
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return Frontmatter(), content

    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() in {"---", "..."}:
            end_idx = idx
            break

    if end_idx is None:
        return Frontmatter(), content

    fm_lines = lines[1:end_idx]
    body = "".join(lines[end_idx + 1 :]).lstrip("\r\n")

    meta = Frontmatter()
    current_list_key: str | None = None

    for raw_line in fm_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_list_key and stripped.startswith("- "):
            item = _strip_quotes(stripped[2:])
            if current_list_key == "tags" and item:
                meta.tags.append(item)
            continue

        current_list_key = None
        if ":" not in raw_line:
            continue

        key, raw_val = raw_line.split(":", 1)
        key = key.strip().lower()
        val = raw_val.strip()

        if key == "title" and val:
            meta.title = _strip_quotes(val)
        elif key == "emoji" and val:
            meta.emoji = _strip_quotes(val)
        elif key == "order" and val:
            try:
                meta.order = int(_strip_quotes(val))
            except ValueError:
                pass
        elif key == "description" and val:
            meta.description = _strip_quotes(val)
        elif key == "draft" and val:
            meta.draft = _parse_bool(_strip_quotes(val))
        elif key == "tags":
            if val:
                meta.tags = _parse_tags(val)
            else:
                current_list_key = "tags"
        else:
            meta.extra[key] = _strip_quotes(val)

    return meta, body