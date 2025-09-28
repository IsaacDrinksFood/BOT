"""Core logic for turning research notes into a ready-to-use e-book template."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import re
from typing import Iterable, List, Sequence


@dataclass
class SubSection:
    """Represents a subsection within a chapter of the research notes."""

    title: str
    content: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short textual summary derived from the subsection content."""

        for paragraph in self._paragraphs():
            sentences = _split_sentences(paragraph)
            if sentences:
                return sentences[0]
        return "Add a summary that captures the essence of this subsection."

    def bullet_points(self) -> List[str]:
        """Return the content normalised as bullet points."""

        bullets: List[str] = []
        buffer: List[str] = []
        for line in self.content:
            stripped = line.strip()
            if not stripped:
                if buffer:
                    bullets.append(" ".join(buffer).strip())
                    buffer.clear()
                continue
            if stripped.startswith(('- ', '* ', '+ ', '•')):
                if buffer:
                    bullets.append(" ".join(buffer).strip())
                    buffer.clear()
                bullets.append(stripped.lstrip('-*+• ').strip())
            else:
                buffer.append(stripped)
        if buffer:
            bullets.append(" ".join(buffer).strip())
        if not bullets:
            return [
                "Break this section into clear bullet points to highlight the major learnings."
            ]
        return bullets

    def _paragraphs(self) -> Iterable[str]:
        paragraph: List[str] = []
        for line in self.content:
            if line.strip():
                paragraph.append(line.strip())
            elif paragraph:
                yield " ".join(paragraph)
                paragraph.clear()
        if paragraph:
            yield " ".join(paragraph)


@dataclass
class Chapter:
    """A single chapter consisting of notes and subsections."""

    title: str
    notes: List[str] = field(default_factory=list)
    subsections: List[SubSection] = field(default_factory=list)

    def summary(self) -> str:
        """Return a heuristic summary for the chapter."""

        for paragraph in self._paragraphs():
            sentences = _split_sentences(paragraph)
            if sentences:
                first_sentence = sentences[0]
                if len(sentences) > 1:
                    return f"{first_sentence} {sentences[1]}"
                return first_sentence
        for subsection in self.subsections:
            summary = subsection.summary()
            if summary:
                return summary
        return "Provide a concise overview of the chapter's purpose and promise."

    def highlights(self) -> List[str]:
        """Aggregate bullet points from the chapter and its subsections."""

        highlights: List[str] = []
        if self.notes:
            highlights.extend(_normalise_bullets(self.notes))
        for subsection in self.subsections:
            for bullet in subsection.bullet_points():
                highlights.append(f"{subsection.title}: {bullet}")
        if not highlights:
            return [
                "List the most important insights readers should remember from this chapter."
            ]
        return highlights

    def _paragraphs(self) -> Iterable[str]:
        paragraph: List[str] = []
        for line in self.notes:
            if line.strip():
                paragraph.append(line.strip())
            elif paragraph:
                yield " ".join(paragraph)
                paragraph.clear()
        if paragraph:
            yield " ".join(paragraph)


class ResearchParser:
    """Parse research notes that follow a Markdown-like structure."""

    heading_pattern = re.compile(r"^(?P<hashes>#+)\s+(?P<title>.+?)\s*$")

    def parse(self, text: str) -> List[Chapter]:
        """Parse *text* into a list of :class:`Chapter` instances."""

        chapters: List[Chapter] = []
        current_chapter: Chapter | None = None
        current_subsection: SubSection | None = None

        def finalise_subsection() -> None:
            nonlocal current_subsection
            if current_subsection and current_chapter:
                current_chapter.subsections.append(current_subsection)
            current_subsection = None

        def finalise_chapter() -> None:
            nonlocal current_chapter
            if current_chapter:
                finalise_subsection()
                chapters.append(current_chapter)
            current_chapter = None

        for raw_line in text.splitlines():
            match = self.heading_pattern.match(raw_line)
            if match:
                level = len(match.group("hashes"))
                title = match.group("title").strip()
                if level <= 1:
                    finalise_chapter()
                    current_chapter = Chapter(title=title)
                    current_subsection = None
                elif level == 2:
                    if current_chapter is None:
                        current_chapter = Chapter(title=title)
                    finalise_subsection()
                    current_subsection = SubSection(title=title)
                else:
                    # Treat deeper headings as plain content for the current subsection.
                    if current_subsection is None:
                        if current_chapter is None:
                            current_chapter = Chapter(title="General Research")
                        current_subsection = SubSection(title=title)
                    current_subsection.content.append(title)
                continue

            line = raw_line.rstrip()
            if current_subsection is not None:
                current_subsection.content.append(line)
            elif current_chapter is not None:
                current_chapter.notes.append(line)
            else:
                # Notes encountered before any heading will be placed in a default chapter.
                current_chapter = Chapter(title="General Research", notes=[line])

        finalise_chapter()
        if not chapters and current_chapter:
            chapters.append(current_chapter)
        return chapters


class EbookTemplateBuilder:
    """Build an e-book template from parsed research notes."""

    def __init__(
        self,
        title: str,
        author: str,
        subtitle: str | None = None,
        include_date: bool = True,
    ) -> None:
        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.include_date = include_date

    def build(self, chapters: Sequence[Chapter]) -> str:
        """Return the rendered e-book template as a Markdown string."""

        lines: List[str] = []
        lines.append(f"# {self.title}")
        if self.subtitle:
            lines.append(f"**Subtitle:** {self.subtitle}")
        lines.append(f"**Author:** {self.author}")
        if self.include_date:
            lines.append(f"**Last Updated:** {date.today().isoformat()}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.extend(self._build_table_of_contents(chapters))
        lines.append("---")
        lines.append("")
        for index, chapter in enumerate(chapters, start=1):
            lines.extend(self._build_chapter(index, chapter))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _build_table_of_contents(self, chapters: Sequence[Chapter]) -> List[str]:
        if not chapters:
            return ["## Table of Contents", "1. Add at least one chapter to the manuscript.", ""]
        toc_lines = ["## Table of Contents"]
        for idx, chapter in enumerate(chapters, start=1):
            entry = f"{idx}. {chapter.title}"
            if chapter.subsections:
                toc_lines.append(entry)
                for subsection in chapter.subsections:
                    toc_lines.append(f"   - {subsection.title}")
            else:
                toc_lines.append(entry)
        toc_lines.append("")
        return toc_lines

    def _build_chapter(self, index: int, chapter: Chapter) -> List[str]:
        lines = [f"## Chapter {index}: {chapter.title}"]
        lines.append("")
        lines.append("### Purpose of this Chapter")
        lines.append(chapter.summary())
        lines.append("")
        lines.append("### Research Highlights")
        for highlight in chapter.highlights():
            lines.append(f"- {highlight}")
        lines.append("")
        lines.append("### Suggested Flow")
        lines.append(
            "Use this space to map the narrative arc. Connect the opening hook, key insights,"
            " and closing transformation in a logical order."
        )
        lines.append("")
        lines.append("### Draft Section")
        lines.append(
            "Write your draft content here, weaving in the research, stories, and exercises."
        )
        lines.append("")
        lines.append("### Calls to Action")
        lines.append("- Outline practical steps readers can implement immediately.")
        lines.append("- Recommend tools, frameworks, or reflection prompts.")
        lines.append("")
        lines.append("### Additional Notes")
        lines.append(
            "Capture supporting data, anecdotes, or expert quotes that didn't fit elsewhere."
        )
        lines.append("")
        if chapter.subsections:
            lines.append("### Reference Subsections")
            for subsection in chapter.subsections:
                lines.append(f"#### {subsection.title}")
                lines.append(f"Summary: {subsection.summary()}")
                lines.append("Key Points:")
                for point in subsection.bullet_points():
                    lines.append(f"- {point}")
                lines.append("")
        return lines


def _split_sentences(text: str) -> List[str]:
    """Very small helper to split text into sentences."""

    if not text:
        return []
    candidates = re.split(r"(?<=[.!?])\s+", text)
    return [candidate.strip() for candidate in candidates if candidate.strip()]


def _normalise_bullets(lines: Iterable[str]) -> List[str]:
    bullets: List[str] = []
    buffer: List[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            if buffer:
                bullets.append(" ".join(buffer).strip())
                buffer.clear()
            continue
        if stripped.startswith(('- ', '* ', '+ ', '•')):
            if buffer:
                bullets.append(" ".join(buffer).strip())
                buffer.clear()
            bullets.append(stripped.lstrip('-*+• ').strip())
        else:
            buffer.append(stripped)
    if buffer:
        bullets.append(" ".join(buffer).strip())
    if not bullets:
        return []
    return bullets
