# Research-to-Ebook Template Generator

This repository contains a small command line utility that reshapes raw research notes
into a ready-to-write e-book template. Feed it Markdown notes with headings and bullet
points, and it will organise them into chapters with summaries, highlight lists, calls to
action, and dedicated drafting spaces.

## Features

- Parses Markdown research notes into chapters and subsections.
- Generates a structured Markdown template with table of contents, chapter scaffolding,
  and reference subsections.
- Works from files or standard input, making it easy to integrate into note-taking
  workflows.

## Getting Started

Install the package locally in editable mode (optional) and run the CLI:

```bash
pip install -e .
python -m ebook_structurer.cli notes.md --title "My Ebook" --author "You"
```

Or pipe notes directly:

```bash
cat notes.md | python -m ebook_structurer.cli --title "My Ebook" --author "You"
```

Pass `--subtitle` to add a subtitle or `--no-date` to hide the generated timestamp.

## Development

Run the test suite with:

```bash
python -m pytest
```
