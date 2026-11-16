from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from emdg.frontmatter import parse_frontmatter
from emdg.scanner import DocItem, DocSection, ScanResult, humanize_name

HTML_TEMPLATE = Path(__file__).with_name("template.html").read_text(encoding="utf-8")

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


def _parse_hex_color(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value):
        raise ValueError("primary_color must be a hex color in #RGB or #RRGGBB format")
    digits = value[1:]
    if len(digits) == 3:
        digits = "".join(char * 2 for char in digits)
    return (
        int(digits[0:2], 16),
        int(digits[2:4], 16),
        int(digits[4:6], 16),
    )


def _format_hex_color(color: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def _relative_luminance(color: tuple[int, int, int]) -> float:
    channels: list[float] = []
    for channel in color:
        value = channel / 255
        channels.append(
            value / 12.92
            if value <= 0.04045
            else ((value + 0.055) / 1.055) ** 2.4
        )
    return sum(
        weight * channel
        for weight, channel in zip((0.2126, 0.7152, 0.0722), channels)
    )


def _contrast_ratio(
    first: tuple[int, int, int], second: tuple[int, int, int]
) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def _mix_color(
    color: tuple[int, int, int], target: tuple[int, int, int], target_weight: float
) -> tuple[int, int, int]:
    return (
        round(color[0] * (1 - target_weight) + target[0] * target_weight),
        round(color[1] * (1 - target_weight) + target[1] * target_weight),
        round(color[2] * (1 - target_weight) + target[2] * target_weight),
    )


def _accent_for_background(
    primary: tuple[int, int, int], background: tuple[int, int, int]
) -> tuple[int, int, int]:
    if _contrast_ratio(primary, background) >= 4.5:
        return primary

    endpoint = (
        (0, 0, 0)
        if _relative_luminance(background) > 0.5
        else (255, 255, 255)
    )
    lower, upper = 0.0, 1.0
    for _ in range(24):
        weight = (lower + upper) / 2
        candidate = _mix_color(primary, endpoint, weight)
        if _contrast_ratio(candidate, background) >= 4.55:
            upper = weight
        else:
            lower = weight
    return _mix_color(primary, endpoint, upper)


def _accent_palette(primary_color: str) -> dict[str, str]:
    primary = _parse_hex_color(primary_color)
    light_soft = _mix_color(primary, (255, 255, 255), 0.94)
    dark_soft = _mix_color(primary, (40, 40, 40), 0.94)
    light = _accent_for_background(primary, light_soft)
    dark = _accent_for_background(primary, dark_soft)
    return {
        "__PRIMARY_ACCENT_LIGHT__": _format_hex_color(light),
        "__PRIMARY_ACCENT_DARK__": _format_hex_color(dark),
        "__PRIMARY_SOFT_LIGHT__": _format_hex_color(light_soft),
        "__PRIMARY_SOFT_DARK__": _format_hex_color(dark_soft),
    }


def generate_html(
    scan_result: ScanResult,
    output_path: str | Path = "docs.html",
    *,
    title: str | None = None,
    theme: str = "auto",
    primary_color: str = "#2563eb",
) -> Path:
    """Build a single-file HTML documentation page from a ScanResult."""
    if theme not in {"auto", "light", "dark"}:
        raise ValueError("theme must be 'auto', 'light', or 'dark'")
    accent_palette = _accent_palette(primary_color)

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
        **accent_palette,
    }
    final_html = re.sub(
        r"__SITE_TITLE__|__DOCS_JSON__|__INITIAL_THEME__|"
        r"__PRIMARY_ACCENT_LIGHT__|__PRIMARY_ACCENT_DARK__|"
        r"__PRIMARY_SOFT_LIGHT__|__PRIMARY_SOFT_DARK__",
        lambda match: replacements[match.group(0)],
        HTML_TEMPLATE,
    )

    out = Path(output_path).resolve()
    out.write_text(final_html, encoding="utf-8")
    return out