from __future__ import annotations

import argparse
import logging
import os
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Sequence

from emdg.generator import generate_html
from emdg.scanner import DEFAULT_IGNORE, scan_docs

LOGGER = logging.getLogger("emdg")
WATCH_INTERVAL = 0.5


def _arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="emdg",
        description="Build a single-page HTML site from Markdown files.",
    )
    parser.add_argument("source", nargs="?", default=".", help="Markdown source directory")
    parser.add_argument("-o", "--output", default="docs.html", help="HTML output path")
    parser.add_argument("-t", "--title", help="Site title")
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        default=[],
        metavar="NAME",
        help="Ignore a file or directory name (may be repeated)",
    )
    parser.add_argument(
        "--theme", choices=("auto", "light", "dark"), default="auto", help="Initial theme"
    )
    parser.add_argument(
        "--primary-color",
        default="#2563eb",
        metavar="HEX",
        help="Primary accent color in #RGB or #RRGGBB format",
    )
    parser.add_argument("--serve", action="store_true", help="Serve the generated site locally")
    parser.add_argument("--watch", action="store_true", help="Rebuild when Markdown files change")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output")
    return parser.parse_args(argv)


def _source_snapshot(source: Path, ignore: set[str]) -> tuple[tuple[str, int, int], ...]:
    files: list[tuple[str, int, int]] = []
    for current, directories, filenames in os.walk(source):
        directories[:] = sorted(
            name for name in directories if name not in ignore and not name.startswith(".")
        )
        for filename in filenames:
            path = Path(current, filename)
            if filename.startswith(".") or path.suffix.lower() != ".md":
                continue
            if filename in ignore:
                continue
            stat = path.stat()
            files.append((path.relative_to(source).as_posix(), stat.st_mtime_ns, stat.st_size))
    return tuple(sorted(files))


def _watch(
    source: Path,
    output: Path,
    title: str | None,
    theme: str,
    ignore: set[str],
    primary_color: str = "#2563eb",
) -> None:
    previous = _source_snapshot(source, ignore)
    LOGGER.info("Watching %s for Markdown changes", source)
    while True:
        time.sleep(WATCH_INTERVAL)
        current = _source_snapshot(source, ignore)
        if current != previous:
            generate_html(
                scan_docs(source, ignore=ignore),
                output,
                title=title,
                theme=theme,
                primary_color=primary_color,
            )
            LOGGER.info("Rebuilt %s", output)
            previous = current


def _serve(
    output: Path,
    watch: bool,
    source: Path,
    title: str | None,
    theme: str,
    ignore: set[str],
    primary_color: str = "#2563eb",
) -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=str(output.parent))
    server = ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    LOGGER.info("Serving %s at http://127.0.0.1:8000/%s", output.name, output.name)

    if not watch:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return

    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        _watch(source, output, title, theme, ignore, primary_color)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()


def main(argv: Sequence[str] | None = None) -> int:
    args = _arguments(argv)
    logging.basicConfig(
        level=(
            logging.DEBUG
            if args.verbose > 1
            else logging.INFO
            if args.verbose
            else logging.WARNING
        ),
        format="%(levelname)s: %(message)s",
    )
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    ignore = set(DEFAULT_IGNORE).union(args.ignore)

    try:
        result = scan_docs(source, ignore=ignore)
        output = generate_html(
            result,
            output,
            title=args.title,
            theme=args.theme,
            primary_color=args.primary_color,
        )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"emdg: {exc}") from exc

    LOGGER.info("Generated %s", output)
    if args.serve:
        _serve(
            output,
            args.watch,
            source,
            args.title,
            args.theme,
            ignore,
            args.primary_color,
        )
    elif args.watch:
        try:
            _watch(source, output, args.title, args.theme, ignore, args.primary_color)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
