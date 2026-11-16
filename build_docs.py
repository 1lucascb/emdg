from pathlib import Path

from emdg import generate_html, scan_docs


ROOT = Path(__file__).resolve().parent


def main() -> None:
    docs = scan_docs(ROOT / "docs")
    output = generate_html(docs, ROOT / "docs.html")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()
