from datetime import date

from ebook_structurer.builder import EbookTemplateBuilder, ResearchParser


SAMPLE_NOTES = """
# Foundations of Deep Focus
Maintaining focus is a learnable skill. Train the mind like a muscle.

## Science of Attention
- Neuroplasticity enables change.
- Focus benefits from deliberate rest.

## Rituals
Morning routines help prime the brain for sustained effort.

# Designing High-Impact Chapters
Start by clarifying the reader's transformation.
""".strip()


def test_parser_creates_chapters_and_subsections():
    chapters = ResearchParser().parse(SAMPLE_NOTES)
    assert len(chapters) == 2
    assert chapters[0].title == "Foundations of Deep Focus"
    assert len(chapters[0].subsections) == 2
    assert chapters[0].subsections[0].title == "Science of Attention"
    assert chapters[0].subsections[0].bullet_points()[0] == "Neuroplasticity enables change."


def test_builder_generates_markdown_template():
    chapters = ResearchParser().parse(SAMPLE_NOTES)
    builder = EbookTemplateBuilder(
        title="Deep Focus Blueprint",
        author="Ada Example",
        subtitle="Turn research into ready-to-write chapters",
        include_date=False,
    )
    template = builder.build(chapters)

    assert template.startswith("# Deep Focus Blueprint")
    assert "## Table of Contents" in template
    assert "## Chapter 1: Foundations of Deep Focus" in template
    assert "### Research Highlights" in template
    assert "Science of Attention: Neuroplasticity enables change." in template
    assert "### Reference Subsections" in template
