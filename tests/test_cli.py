import json
import re
from pathlib import Path

import emdg.cli as cli
import pytest

from emdg.cli import main


def test_cli_default_and_custom_options(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "docs"
    source.mkdir()
    (source / "intro.md").write_text("# Hello\n", encoding="utf-8")

    assert main([str(source)]) == 0
    default_html = (tmp_path / "docs.html").read_text(encoding="utf-8")
    assert "Intro" in default_html

    output = tmp_path / "custom.html"
    assert main(
        [
            str(source),
            "--output",
            str(output),
            "--title",
            "Custom Title",
            "--theme",
            "light",
        ]
    ) == 0

    html = output.read_text(encoding="utf-8")
    assert "<title>Custom Title</title>" in html
    assert 'const initialTheme = "light"' in html
    match = re.search(r"window\.__DOCS__ = (.*?);\s*const formatLabel", html, re.DOTALL)
    assert match and json.loads(match.group(1))["title"] == "Custom Title"


def test_watch_rebuilds_when_source_metadata_changes(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "docs"
    source.mkdir()
    snapshots = iter(
        [
            (("guide/index.md", 1, 10),),
            (("guide/index.md", 2, 10),),
        ]
    )
    generated = []

    def snapshot(*args):
        try:
            return next(snapshots)
        except StopIteration:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli, "_source_snapshot", snapshot)
    monkeypatch.setattr(cli.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        cli,
        "generate_html",
        lambda *args, **kwargs: generated.append((args, kwargs)),
    )

    with pytest.raises(KeyboardInterrupt):
        cli._watch(source, tmp_path / "site.html", "Docs", "dark", set())

    assert len(generated) == 1
    assert generated[0][0][0].root == source.resolve()
    assert generated[0][1] == {"title": "Docs", "theme": "dark"}


def test_serve_closes_server_after_interrupt(tmp_path: Path, monkeypatch) -> None:
    servers = []

    class Server:
        def __init__(self, address, handler):
            self.address = address
            self.closed = False
            servers.append(self)

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            self.closed = True

    monkeypatch.setattr(cli, "ThreadingHTTPServer", Server)

    cli._serve(
        tmp_path / "site.html",
        False,
        tmp_path,
        None,
        "auto",
        set(),
    )

    server = servers[0]
    assert server.address == ("127.0.0.1", 8000)
    assert server.closed
