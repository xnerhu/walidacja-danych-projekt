# src/utils/report.py
"""
Report generation utilities for creating Markdown reports.
Extends MarkdownBuilder with data analysis specific features.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Union, Any
import os
from datetime import datetime

from constants import REPORT_DIR
from .df import df_info, df_missing_summary, df_describe_all


# =============================================================================
# ReportBuilder Class
# =============================================================================


class ReportBuilder:
    """
    Builder for creating Markdown reports with tables, figures, and analysis sections.
    """

    def __init__(self, title: Optional[str] = None):
        """
        Initialize report builder.

        Args:
            title: Report title (optional, adds H1 header)
        """
        self.contents: List[str] = []
        self._figure_count = 0
        self._table_count = 0

        if title:
            self.add_heading(title, level=1)
            self.add_paragraph(
                f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
            )
            self.add_separator()

    def add_heading(self, text: str, level: int = 1) -> "ReportBuilder":
        """Add heading (H1-H6)."""
        prefix = "#" * min(max(level, 1), 6)
        self.contents.append(f"{prefix} {text}\n")
        return self

    def add_paragraph(self, text: str) -> "ReportBuilder":
        """Add paragraph text."""
        self.contents.append(f"{text}\n")
        return self

    def add_text(self, text: str) -> "ReportBuilder":
        """Add raw text without extra newline."""
        self.contents.append(text)
        return self

    def add_newline(self, count: int = 1) -> "ReportBuilder":
        """Add blank lines."""
        self.contents.append("\n" * count)
        return self

    def add_separator(self) -> "ReportBuilder":
        """Add horizontal rule."""
        self.contents.append("\n---\n")
        return self

    def add_bullet(self, text: str, indent: int = 0) -> "ReportBuilder":
        """Add bullet point."""
        prefix = "  " * indent
        self.contents.append(f"{prefix}- {text}\n")
        return self

    def add_numbered(self, text: str, number: int) -> "ReportBuilder":
        """Add numbered item."""
        self.contents.append(f"{number}. {text}\n")
        return self

    def add_code(self, code: str, language: str = "") -> "ReportBuilder":
        """Add code block."""
        self.contents.append(f"```{language}\n{code}\n```\n")
        return self

    def add_inline_code(self, text: str) -> str:
        """Return inline code formatted string (doesn't add to report)."""
        return f"`{text}`"

    def add_quote(self, text: str) -> "ReportBuilder":
        """Add blockquote."""
        lines = text.split("\n")
        quoted = "\n".join(f"> {line}" for line in lines)
        self.contents.append(f"{quoted}\n")
        return self

    def add_bold(self, text: str) -> str:
        """Return bold formatted string (doesn't add to report)."""
        return f"**{text}**"

    def add_italic(self, text: str) -> str:
        """Return italic formatted string (doesn't add to report)."""
        return f"*{text}*"

    def add_link(self, text: str, url: str) -> "ReportBuilder":
        """Add link."""
        self.contents.append(f"[{text}]({url})\n")
        return self

    # =========================================================================
    # Tables
    # =========================================================================

    def add_table(
        self,
        df: pd.DataFrame,
        caption: Optional[str] = None,
        max_rows: Optional[int] = None,
        float_format: str = ":.2f",
    ) -> "ReportBuilder":
        """
        Add DataFrame as Markdown table.

        Args:
            df: DataFrame to display
            caption: Table caption
            max_rows: Maximum rows to display (truncates if exceeded)
            float_format: Format string for floats
        """
        self._table_count += 1

        if caption:
            self.add_paragraph(f"**Table {self._table_count}:** {caption}")

        display_df = df.copy()

        # Truncate if needed
        if max_rows and len(display_df) > max_rows:
            display_df = display_df.head(max_rows)
            truncated = True
        else:
            truncated = False

        # Format floats
        for col in display_df.select_dtypes(include=[np.number]).columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"{x:{float_format}}" if pd.notna(x) else ""
            )

        table_md = display_df.to_markdown(index=False)
        self.contents.append(f"{table_md}\n")

        if truncated:
            self.add_paragraph(f"*... showing {max_rows} of {len(df)} rows*")

        return self

    def add_simple_table(
        self, headers: List[str], rows: List[List[Any]]
    ) -> "ReportBuilder":
        """
        Add simple table from headers and rows.

        Args:
            headers: Column headers
            rows: List of row values
        """
        df = pd.DataFrame(rows, columns=headers)
        return self.add_table(df)

    def add_key_value_table(
        self, data: dict, title: Optional[str] = None
    ) -> "ReportBuilder":
        """
        Add key-value pairs as two-column table.

        Args:
            data: Dictionary of key-value pairs
            title: Optional title
        """
        if title:
            self.add_heading(title, level=4)

        df = pd.DataFrame(list(data.items()), columns=["Metric", "Value"])
        return self.add_table(df)

    # =========================================================================
    # Figures
    # =========================================================================

    def add_figure(
        self,
        path: str,
        caption: Optional[str] = None,
        alt: Optional[str] = None,
        width: Optional[str] = None,
    ) -> "ReportBuilder":
        """
        Add figure/image.

        Args:
            path: Path to image (relative to report or absolute)
            caption: Figure caption
            alt: Alt text for accessibility
            width: Optional width (HTML only)
        """
        self._figure_count += 1

        alt_text = alt or caption or f"Figure {self._figure_count}"

        if width:
            # Use HTML for width control
            self.contents.append(
                f'<img src="{path}" alt="{alt_text}" width="{width}" />\n'
            )
        else:
            self.contents.append(f"![{alt_text}]({path})\n")

        if caption:
            self.add_paragraph(f"*Figure {self._figure_count}: {caption}*")

        return self

    # =========================================================================
    # Data Analysis Sections
    # =========================================================================

    def add_dataset_overview(
        self, df: pd.DataFrame, name: str = "Dataset"
    ) -> "ReportBuilder":
        """
        Add comprehensive dataset overview section.

        Includes: dimensions, memory, dtypes, missing summary.
        """
        self.add_heading(f"{name} Overview", level=2)

        info = df_info(df)

        self.add_key_value_table(
            {
                "Rows": f"{info['rows']:,}",
                "Columns": info["cols"],
                "Memory": f"{info['memory_mb']:.2f} MB",
                "Total Missing": f"{info['missing_total']:,}",
                "Missing %": f"{info['missing_pct']:.2f}%",
            }
        )

        # Data types
        self.add_heading("Data Types", level=3)
        dtype_df = pd.DataFrame(list(info["dtypes"].items()), columns=["Type", "Count"])
        self.add_table(dtype_df)

        return self

    def add_missing_summary(
        self, df: pd.DataFrame, threshold: float = 0.0
    ) -> "ReportBuilder":
        """
        Add missing data summary section.

        Args:
            threshold: Only show columns with missing % above this threshold
        """
        self.add_heading("Missing Data Summary", level=3)

        summary = df_missing_summary(df)
        summary = summary[summary["missing_pct"] > threshold]

        if len(summary) == 0:
            self.add_paragraph("No missing values found.")
        else:
            self.add_paragraph(
                f"Found {len(summary)} columns with missing values (>{threshold}%):"
            )
            self.add_table(summary, max_rows=30)

        return self

    def add_statistics_summary(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        title: str = "Descriptive Statistics",
    ) -> "ReportBuilder":
        """
        Add descriptive statistics table.

        Args:
            columns: Columns to include (default: all numeric)
            title: Section title
        """
        self.add_heading(title, level=3)

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        stats = df[columns].describe().T
        stats = stats.round(2)
        stats.index.name = "Variable"
        stats = stats.reset_index()

        self.add_table(stats)
        return self

    def add_correlation_summary(
        self, df: pd.DataFrame, top_n: int = 10, threshold: float = 0.5
    ) -> "ReportBuilder":
        """
        Add top correlations summary.

        Args:
            top_n: Number of top correlations to show
            threshold: Minimum absolute correlation to include
        """
        from .df import top_correlations

        self.add_heading("Top Correlations", level=3)

        corr_df = top_correlations(df, n=top_n)
        corr_df = corr_df[corr_df["correlation"].abs() >= threshold]

        if len(corr_df) == 0:
            self.add_paragraph(f"No correlations above {threshold} threshold.")
        else:
            self.add_table(corr_df)

        return self

    def add_value_counts(
        self,
        df: pd.DataFrame,
        col: str,
        top_n: int = 10,
        title: Optional[str] = None,
    ) -> "ReportBuilder":
        """Add value counts for categorical column."""
        title = title or f"Value Counts: {col}"
        self.add_heading(title, level=4)

        counts = df[col].value_counts().head(top_n).reset_index()
        counts.columns = [col, "Count"]
        counts["Percent"] = (counts["Count"] / len(df) * 100).round(2)

        self.add_table(counts)
        return self

    # =========================================================================
    # Special Boxes
    # =========================================================================

    def add_info_box(self, text: str) -> "ReportBuilder":
        """Add info box."""
        self.add_quote(f"ℹ️ **Info:** {text}")
        return self

    def add_warning_box(self, text: str) -> "ReportBuilder":
        """Add warning box."""
        self.add_quote(f"⚠️ **Warning:** {text}")
        return self

    def add_success_box(self, text: str) -> "ReportBuilder":
        """Add success box."""
        self.add_quote(f"✅ **Success:** {text}")
        return self

    def add_error_box(self, text: str) -> "ReportBuilder":
        """Add error box."""
        self.add_quote(f"❌ **Error:** {text}")
        return self

    # =========================================================================
    # Collapsible Sections
    # =========================================================================

    def add_collapsible(
        self, title: str, content: str, open_by_default: bool = False
    ) -> "ReportBuilder":
        """
        Add collapsible/expandable section (HTML details tag).

        Args:
            title: Section title (always visible)
            content: Content to show/hide
            open_by_default: Whether section starts expanded
        """
        open_attr = " open" if open_by_default else ""
        self.contents.append(
            f"<details{open_attr}>\n<summary>{title}</summary>\n\n{content}\n\n</details>\n"
        )
        return self

    # =========================================================================
    # Output
    # =========================================================================

    def to_string(self) -> str:
        """Get report as string."""
        return "\n".join(self.contents)

    def save(self, path: str) -> str:
        """
        Save report to file.

        Args:
            path: Output path (relative to REPORT_DIR if not absolute)

        Returns:
            Absolute path to saved file
        """
        if not os.path.isabs(path):
            path = os.path.join(REPORT_DIR, path)

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_string())

        print(f"Report saved: {path}")
        return path

    def __str__(self) -> str:
        return self.to_string()


# =============================================================================
# Standalone Functions
# =============================================================================


def generate_variable_report(
    df: pd.DataFrame, col: str, include_plot: bool = False
) -> str:
    """
    Generate a complete report for a single variable.

    Args:
        df: DataFrame
        col: Column name
        include_plot: Whether to include histogram path placeholder

    Returns:
        Markdown string
    """
    report = ReportBuilder()
    report.add_heading(f"Variable: {col}", level=3)

    # Basic info
    dtype = str(df[col].dtype)
    non_null = df[col].notna().sum()
    null_count = df[col].isna().sum()
    null_pct = null_count / len(df) * 100
    unique = df[col].nunique()

    report.add_key_value_table(
        {
            "Data Type": dtype,
            "Non-Null Count": f"{non_null:,}",
            "Missing Count": f"{null_count:,}",
            "Missing %": f"{null_pct:.2f}%",
            "Unique Values": f"{unique:,}",
        }
    )

    # Statistics for numeric
    if pd.api.types.is_numeric_dtype(df[col]):
        report.add_heading("Statistics", level=4)
        stats = df[col].describe()
        report.add_key_value_table(
            {
                "Mean": f"{stats['mean']:.4f}",
                "Std": f"{stats['std']:.4f}",
                "Min": f"{stats['min']:.4f}",
                "25%": f"{stats['25%']:.4f}",
                "Median": f"{stats['50%']:.4f}",
                "75%": f"{stats['75%']:.4f}",
                "Max": f"{stats['max']:.4f}",
            }
        )

        if include_plot:
            report.add_figure(f"figures/{col}_histogram.png", f"Distribution of {col}")

    # Value counts for categorical
    else:
        report.add_value_counts(df, col, top_n=10)

    return report.to_string()


def generate_dataset_summary(df: pd.DataFrame, name: str = "Dataset") -> str:
    """
    Generate a quick dataset summary.

    Returns:
        Markdown string
    """
    report = ReportBuilder(title=f"{name} Summary")
    report.add_dataset_overview(df, name)
    report.add_missing_summary(df)
    report.add_statistics_summary(df)

    return report.to_string()


def create_codebook(
    df: pd.DataFrame,
    descriptions: Optional[dict] = None,
    title: str = "Codebook",
) -> str:
    """
    Generate a codebook (data dictionary) for the dataset.

    Args:
        df: DataFrame
        descriptions: Dict mapping column names to descriptions
        title: Codebook title

    Returns:
        Markdown string
    """
    descriptions = descriptions or {}

    report = ReportBuilder(title=title)

    report.add_paragraph(
        f"This codebook describes the variables in the dataset ({len(df.columns)} columns, {len(df):,} rows)."
    )

    report.add_separator()

    rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_pct = df[col].isna().sum() / len(df) * 100
        unique = df[col].nunique()

        # Sample values
        sample_vals = df[col].dropna().head(3).tolist()
        sample_str = ", ".join(str(v)[:20] for v in sample_vals)

        desc = descriptions.get(col, "")

        rows.append(
            {
                "Variable": col,
                "Type": dtype,
                "Non-Null": f"{non_null:,}",
                "Missing %": f"{null_pct:.1f}%",
                "Unique": unique,
                "Sample": sample_str,
                "Description": desc,
            }
        )

    codebook_df = pd.DataFrame(rows)
    report.add_table(codebook_df)

    return report.to_string()
