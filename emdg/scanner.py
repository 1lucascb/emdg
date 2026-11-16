from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from emdg.frontmatter import Frontmatter, parse_frontmatter

DEFAULT_IGNORE: frozenset[str] = frozenset({
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build",
})


@dataclass(slots=True)
class DocItem:
    title: str
    slug: str
    path: Path
    relative_path: Path
    emoji: str | None = None
    order: int = 999
    description: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DocSection:
    title: str
    slug: str
    path: Path
    relative_path: Path
    emoji: str | None = None
    order: int = 999
    description: str | None = None
    items: list[DocItem] = field(default_factory=list)
    subsections: list[DocSection] = field(default_factory=list)
    body: str = ""
    

@dataclass(slots=True)
class ScanResult:
    root: Path
    root_items: list[DocItem] = field(default_factory=list)
    sections: list[DocSection] = field(default_factory=list)
    home: DocItem | None = None


def humanize_name(name: str) -> str:
    """Convert 'how-it-works' or 'user_guide' -> 'How It Works' / 'User Guide'."""
    cleaned = name.replace("-", " ").replace("_", " ").strip()
    return " ".join(word.capitalize() for word in cleaned.split()) if cleaned else name


def _slugify(relative_path: Path) -> str:
    return relative_path.with_suffix("").as_posix().strip("/")


def _should_ignore(entry: Path, ignore: set[str]) -> bool:
    return entry.name in ignore or entry.name.startswith(".")


def _read_meta(file_path: Path) -> Frontmatter:
    raw = file_path.read_text(encoding="utf-8")
    meta, _ = parse_frontmatter(raw)
    return meta


def scan_docs(
    origin: str | Path,
    *,
    ignore: Iterable[str] | None = None,
    extensions: Iterable[str] = (".md",),
) -> ScanResult:
    """
    Recursively scan `origin` for Markdown files and build a section tree.
    Supports frontmatter: title, emoji, order, description, draft, and tags.
    """
    root_path = Path(origin).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Origin directory does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Origin path is not a directory: {root_path}")

    allowed_exts = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions
    }
    ignore_set = set(DEFAULT_IGNORE)
    if ignore:
        ignore_set.update(ignore)

    def _build_item(file_path: Path) -> DocItem | None:
        meta = _read_meta(file_path)
        if meta.draft:
            return None
        rel = file_path.relative_to(root_path)
        return DocItem(
            title=meta.title or humanize_name(file_path.stem),
            slug=_slugify(rel),
            path=file_path,
            relative_path=rel,
            emoji=meta.emoji,
            order=meta.order,
            description=meta.description,
            tags=meta.tags,
        )

    def _scan_dir(current_dir: Path) -> tuple[list[DocItem], list[DocSection]]:
        items: list[DocItem] = []
        subsections: list[DocSection] = []

        for entry in current_dir.iterdir():
            if _should_ignore(entry, ignore_set):
                continue

            if (
                entry.is_file()
                and entry.name not in {"_section.md", "index.md"}
                and entry.suffix.lower() in allowed_exts
            ):
                item = _build_item(entry)
                if item is not None:
                    items.append(item)
            elif entry.is_dir():
                sub_items, sub_sections = _scan_dir(entry)
                if sub_items or sub_sections:
                    rel = entry.relative_to(root_path)
                    # Optional _section.md or index.md inside folder can override section meta
                    section_meta = Frontmatter()
                    section_body = ""
                    for meta_file in ("_section.md", "index.md"):
                        candidate = entry / meta_file
                        if candidate.is_file():
                            raw = candidate.read_text(encoding="utf-8")
                            section_meta, body = parse_frontmatter(raw)
                            if meta_file == "_section.md":
                                section_body = body
                            break

                    subsections.append(
                        DocSection(
                            title=section_meta.title or humanize_name(entry.name),
                            slug=_slugify(rel),
                            path=entry,
                            relative_path=rel,
                            emoji=section_meta.emoji,
                            order=section_meta.order,
                            description=section_meta.description,
                            items=sub_items,
                            subsections=sub_sections,
                            body=section_body,
                        )
                    )

        items.sort(key=lambda i: (i.order, i.title.lower(), i.relative_path.as_posix()))
        subsections.sort(
            key=lambda s: (s.order, s.title.lower(), s.relative_path.as_posix())
        )
        return items, subsections

    root_items, sections = _scan_dir(root_path)
    home = next(
        (item for item in root_items if item.relative_path.name.casefold() == "readme.md"),
        None,
    )
    if home is not None:
        root_items.remove(home)
    return ScanResult(root=root_path, root_items=root_items, sections=sections, home=home)

