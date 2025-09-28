"""Command line interface for generating an e-book template from research notes."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import TextIO

from .builder import EbookTemplateBuilder, ResearchParser


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Transform research notes written in Markdown into a structured e-book template."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to the research notes (defaults to standard input).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output path. Writes to standard output when omitted.",
    )
    parser.add_argument("--title", required=True, help="Title of the e-book.")
    parser.add_argument("--author", required=True, help="Author name to include in the template.")
    parser.add_argument("--subtitle", help="Optional subtitle to display beneath the title.")
    parser.add_argument(
        "--no-date",
        dest="include_date",
        action="store_false",
        help="Omit the auto-generated last-updated date from the template.",
    )
    return parser


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    stdout = stdout or sys.stdout

    notes = _read_notes(args.input)
    chapters = ResearchParser().parse(notes)
    builder = EbookTemplateBuilder(
        title=args.title,
        author=args.author,
        subtitle=args.subtitle,
        include_date=args.include_date,
    )
    template = builder.build(chapters)

    if args.output:
        args.output.write_text(template, encoding="utf-8")
    else:
        stdout.write(template)
    return 0


def _read_notes(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover - manual execution entry point
    raise SystemExit(main())
