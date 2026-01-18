# src/utils/markdown.py
"""
Markdown generation utilities.
Simple functions for creating markdown elements.
"""

import pandas as pd
from typing import Optional, List


# =============================================================================
# Headings
# =============================================================================


def h1(title: str) -> str:
    """Create H1 heading."""
    return f"# {title}\n"


def h2(title: str) -> str:
    """Create H2 heading."""
    return f"## {title}\n"


def h3(title: str) -> str:
    """Create H3 heading."""
    return f"### {title}\n"


def h4(title: str) -> str:
    """Create H4 heading."""
    return f"#### {title}\n"


def h5(title: str) -> str:
    """Create H5 heading."""
    return f"##### {title}\n"


def h6(title: str) -> str:
    """Create H6 heading."""
    return f"###### {title}\n"


def heading(title: str, level: int = 1) -> str:
    """Create heading of specified level (1-6)."""
    level = max(1, min(6, level))
    return f"{'#' * level} {title}\n"


# =============================================================================
# Text Elements
# =============================================================================


def paragraph(text: str) -> str:
    """Create paragraph."""
    return f"{text}\n"


def bold(text: str) -> str:
    """Make text bold."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Make text italic."""
    return f"*{text}*"


def bold_italic(text: str) -> str:
    """Make text bold and italic."""
    return f"***{text}***"


def strikethrough(text: str) -> str:
    """Make text strikethrough."""
    return f"~~{text}~~"


def inline_code(text: str) -> str:
    """Make inline code."""
    return f"`{text}`"


# =============================================================================
# Lists
# =============================================================================


def bullet_item(text: str, indent: int = 0) -> str:
    """Create bullet item."""
    prefix = "  " * indent
    return f"{prefix}- {text}\n"


def numbered_item(text: str, number: int) -> str:
    """Create numbered item."""
    return f"{number}. {text}\n"


def bullet_list(items: List[str]) -> str:
    """Create bullet list from items."""
    return "".join(bullet_item(item) for item in items)


def numbered_list(items: List[str]) -> str:
    """Create numbered list from items."""
    return "".join(numbered_item(item, i + 1) for i, item in enumerate(items))


def checklist_item(text: str, checked: bool = False) -> str:
    """Create checklist item."""
    checkbox = "[x]" if checked else "[ ]"
    return f"- {checkbox} {text}\n"


def checklist(items: List[tuple]) -> str:
    """
    Create checklist from items.

    Args:
        items: List of (text, checked) tuples
    """
    return "".join(checklist_item(text, checked) for text, checked in items)


# =============================================================================
# Code
# =============================================================================


def code_block(code: str, language: str = "") -> str:
    """Create code block."""
    return f"```{language}\n{code}\n```\n"


# =============================================================================
# Links and Images
# =============================================================================


def link(text: str, url: str) -> str:
    """Create link."""
    return f"[{text}]({url})"


def image(path: str, alt: str = "", caption: Optional[str] = None) -> str:
    """
    Create image element.

    Args:
        path: Image path or URL
        alt: Alt text
        caption: Optional caption (displayed below image)
    """
    img = f"![{alt}]({path})\n"
    if caption:
        img += f"*{caption}*\n"
    return img


def reference_link(text: str, ref_id: str) -> str:
    """Create reference-style link."""
    return f"[{text}][{ref_id}]"


def reference_definition(ref_id: str, url: str, title: Optional[str] = None) -> str:
    """Create reference definition."""
    if title:
        return f'[{ref_id}]: {url} "{title}"\n'
    return f"[{ref_id}]: {url}\n"


# =============================================================================
# Structural Elements
# =============================================================================


def horizontal_rule() -> str:
    """Create horizontal rule."""
    return "\n---\n"


def blockquote(text: str) -> str:
    """Create blockquote."""
    lines = text.split("\n")
    return "\n".join(f"> {line}" for line in lines) + "\n"


def nested_blockquote(text: str, level: int = 1) -> str:
    """Create nested blockquote."""
    prefix = "> " * level
    lines = text.split("\n")
    return "\n".join(f"{prefix}{line}" for line in lines) + "\n"


# =============================================================================
# Tables
# =============================================================================


def table(df: pd.DataFrame, index: bool = False) -> str:
    """Create table from DataFrame."""
    return df.to_markdown(index=index) + "\n"


def simple_table(headers: List[str], rows: List[List]) -> str:
    """
    Create simple table from headers and rows.

    Args:
        headers: Column headers
        rows: List of row values
    """
    df = pd.DataFrame(rows, columns=headers)
    return table(df)


def key_value_table(data: dict) -> str:
    """
    Create two-column table from dictionary.

    Args:
        data: Dictionary of key-value pairs
    """
    df = pd.DataFrame(list(data.items()), columns=["Key", "Value"])
    return table(df)


# =============================================================================
# Special Boxes (using blockquotes)
# =============================================================================


def info_box(text: str) -> str:
    """Create info box."""
    return blockquote(f"ℹ️ **Info:** {text}")


def warning_box(text: str) -> str:
    """Create warning box."""
    return blockquote(f"⚠️ **Warning:** {text}")


def success_box(text: str) -> str:
    """Create success box."""
    return blockquote(f"✅ **Success:** {text}")


def error_box(text: str) -> str:
    """Create error box."""
    return blockquote(f"❌ **Error:** {text}")


def tip_box(text: str) -> str:
    """Create tip box."""
    return blockquote(f"💡 **Tip:** {text}")


def note_box(text: str) -> str:
    """Create note box."""
    return blockquote(f"📝 **Note:** {text}")


# =============================================================================
# Collapsible Sections (HTML)
# =============================================================================


def collapsible(title: str, content: str, open_by_default: bool = False) -> str:
    """
    Create collapsible/expandable section.

    Args:
        title: Section title (always visible)
        content: Content to show/hide
        open_by_default: Whether section starts expanded
    """
    open_attr = " open" if open_by_default else ""
    return (
        f"<details{open_attr}>\n<summary>{title}</summary>\n\n{content}\n\n</details>\n"
    )


# =============================================================================
# MarkdownBuilder Class
# =============================================================================


class MarkdownBuilder:
    """Builder class for constructing markdown documents."""

    def __init__(self):
        self.contents = []

    def add(self, markdown: str) -> "MarkdownBuilder":
        """Add markdown content."""
        self.contents.append(markdown)
        return self

    def add_h1(self, title: str) -> "MarkdownBuilder":
        return self.add(h1(title))

    def add_h2(self, title: str) -> "MarkdownBuilder":
        return self.add(h2(title))

    def add_h3(self, title: str) -> "MarkdownBuilder":
        return self.add(h3(title))

    def add_h4(self, title: str) -> "MarkdownBuilder":
        return self.add(h4(title))

    def add_paragraph(self, text: str) -> "MarkdownBuilder":
        return self.add(paragraph(text))

    def add_bullet_list(self, items: List[str]) -> "MarkdownBuilder":
        return self.add(bullet_list(items))

    def add_numbered_list(self, items: List[str]) -> "MarkdownBuilder":
        return self.add(numbered_list(items))

    def add_code_block(self, code: str, language: str = "") -> "MarkdownBuilder":
        return self.add(code_block(code, language))

    def add_table(self, df: pd.DataFrame) -> "MarkdownBuilder":
        return self.add(table(df))

    def add_image(
        self, path: str, alt: str = "", caption: Optional[str] = None
    ) -> "MarkdownBuilder":
        return self.add(image(path, alt, caption))

    def add_horizontal_rule(self) -> "MarkdownBuilder":
        return self.add(horizontal_rule())

    def add_blockquote(self, text: str) -> "MarkdownBuilder":
        return self.add(blockquote(text))

    def add_collapsible(
        self, title: str, content: str, open_by_default: bool = False
    ) -> "MarkdownBuilder":
        return self.add(collapsible(title, content, open_by_default))

    def add_info_box(self, text: str) -> "MarkdownBuilder":
        return self.add(info_box(text))

    def add_warning_box(self, text: str) -> "MarkdownBuilder":
        return self.add(warning_box(text))

    def add_newline(self, count: int = 1) -> "MarkdownBuilder":
        return self.add("\n" * count)

    def to_string(self) -> str:
        """Get markdown as string."""
        return "\n".join(self.contents)

    def save(self, path: str) -> str:
        """Save markdown to file."""
        from pathlib import Path as P

        P(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_string())
        return path

    def __str__(self) -> str:
        return self.to_string()
