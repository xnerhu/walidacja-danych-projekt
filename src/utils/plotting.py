# src/utils/plotting.py
"""
Plotting utilities for EDA and reports.
Standardized charts with consistent styling.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Union, Tuple
import os

from constants import REPORT_DIR

# =============================================================================
# Configuration & Style
# =============================================================================

# Default figure directory
FIGURES_DIR = os.path.join(REPORT_DIR, "figures")


def setup_plotting_style():
    """Set up consistent plotting style for all figures."""
    plt.style.use("seaborn-v0_8-whitegrid")

    plt.rcParams.update(
        {
            # Figure
            "figure.figsize": (10, 6),
            "figure.dpi": 100,
            "figure.facecolor": "white",
            # Font
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            # Lines
            "lines.linewidth": 2,
            "lines.markersize": 6,
            # Grid
            "axes.grid": True,
            "grid.alpha": 0.3,
            # Legend
            "legend.framealpha": 0.9,
            "legend.edgecolor": "gray",
        }
    )

    # Seaborn settings
    sns.set_palette("husl")


def save_figure(
    fig: plt.Figure,
    name: str,
    dpi: int = 150,
    figures_dir: Optional[str] = None,
    formats: List[str] = ["png"],
) -> str:
    """
    Save figure to file(s).

    Args:
        fig: Matplotlib figure
        name: Filename (without extension)
        dpi: Resolution
        figures_dir: Directory to save (default: FIGURES_DIR)
        formats: List of formats to save ('png', 'svg', 'pdf')

    Returns:
        Path to primary saved file (first format)
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    primary_path = None
    for fmt in formats:
        path = os.path.join(figures_dir, f"{name}.{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
        if primary_path is None:
            primary_path = path

    plt.close(fig)
    return primary_path


# =============================================================================
# Distribution Plots
# =============================================================================


def plot_histogram(
    df: pd.DataFrame,
    col: str,
    bins: int = 30,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    kde: bool = True,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """
    Plot histogram with optional KDE.

    Args:
        col: Column to plot
        bins: Number of bins
        title: Plot title (default: column name)
        kde: Whether to overlay KDE
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.histplot(data=df, x=col, bins=bins, kde=kde, ax=ax)

    ax.set_title(title or f"Distribution of {col}")
    ax.set_xlabel(xlabel or col)
    ax.set_ylabel("Count")

    return fig


def plot_boxplot(
    df: pd.DataFrame,
    col: str,
    by: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    orient: str = "v",
) -> plt.Figure:
    """
    Plot boxplot, optionally grouped by category.

    Args:
        col: Numeric column to plot
        by: Categorical column for grouping (optional)
        orient: 'v' for vertical, 'h' for horizontal
    """
    fig, ax = plt.subplots(figsize=figsize)

    if by:
        if orient == "h":
            sns.boxplot(data=df, x=col, y=by, ax=ax)
        else:
            sns.boxplot(data=df, x=by, y=col, ax=ax)
            plt.xticks(rotation=45, ha="right")
    else:
        if orient == "h":
            sns.boxplot(data=df, x=col, ax=ax)
        else:
            sns.boxplot(data=df, y=col, ax=ax)

    ax.set_title(title or f"Boxplot of {col}" + (f" by {by}" if by else ""))

    plt.tight_layout()
    return fig


def plot_kde(
    df: pd.DataFrame,
    col: str,
    hue: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """Plot KDE (density) plot."""
    fig, ax = plt.subplots(figsize=figsize)

    sns.kdeplot(data=df, x=col, hue=hue, fill=True, alpha=0.5, ax=ax)

    ax.set_title(title or f"Density of {col}")
    ax.set_xlabel(col)

    return fig


def plot_multi_histogram(
    df: pd.DataFrame,
    columns: List[str],
    ncols: int = 3,
    bins: int = 30,
    figsize_per_plot: Tuple[int, int] = (4, 3),
) -> plt.Figure:
    """
    Plot multiple histograms in a grid.

    Args:
        columns: List of columns to plot
        ncols: Number of columns in grid
        bins: Number of bins per histogram
    """
    nrows = (len(columns) + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(figsize_per_plot[0] * ncols, figsize_per_plot[1] * nrows)
    )
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for i, col in enumerate(columns):
        if i < len(axes):
            sns.histplot(data=df, x=col, bins=bins, ax=axes[i], kde=True)
            axes[i].set_title(col)
            axes[i].set_xlabel("")

    # Hide empty subplots
    for i in range(len(columns), len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()
    return fig


# =============================================================================
# Correlation Plots
# =============================================================================


def plot_correlation_heatmap(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    title: str = "Correlation Matrix",
    figsize: Tuple[int, int] = (12, 10),
    annot: bool = True,
    cmap: str = "RdBu_r",
    vmin: float = -1,
    vmax: float = 1,
) -> plt.Figure:
    """
    Plot correlation heatmap.

    Args:
        columns: Columns to include (default: all numeric)
        annot: Whether to show correlation values
        cmap: Color map
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    corr = df[columns].corr()

    fig, ax = plt.subplots(figsize=figsize)

    # Create mask for upper triangle (optional, cleaner look)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    sns.heatmap(
        corr,
        mask=mask,
        annot=annot,
        fmt=".2f",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        annot_kws={"size": 8},
    )

    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    size: Optional[str] = None,
    title: Optional[str] = None,
    alpha: float = 0.6,
    figsize: Tuple[int, int] = (10, 8),
    add_regression: bool = False,
) -> plt.Figure:
    """
    Plot scatter plot with optional hue and size encoding.

    Args:
        x: X-axis column
        y: Y-axis column
        hue: Column for color encoding
        size: Column for size encoding
        add_regression: Add regression line
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.scatterplot(data=df, x=x, y=y, hue=hue, size=size, alpha=alpha, ax=ax)

    if add_regression:
        sns.regplot(
            data=df, x=x, y=y, scatter=False, color="red", line_kws={"linestyle": "--"}
        )

    ax.set_title(title or f"{y} vs {x}")

    if hue:
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    return fig


def plot_scatter_matrix(
    df: pd.DataFrame,
    columns: List[str],
    hue: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 12),
) -> plt.Figure:
    """Plot pairwise scatter plots (scatter matrix)."""
    fig = sns.pairplot(
        df[columns + ([hue] if hue else [])].dropna(),
        hue=hue,
        diag_kind="kde",
        plot_kws={"alpha": 0.5},
        height=figsize[0] / len(columns),
    )
    return fig.fig


# =============================================================================
# Time Series Plots
# =============================================================================


def plot_time_series(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    marker: Optional[str] = None,
) -> plt.Figure:
    """
    Plot time series line chart.

    Args:
        x: Time column (e.g., 'year')
        y: Value column
        hue: Column for multiple lines
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.lineplot(data=df, x=x, y=y, hue=hue, marker=marker, ax=ax)

    ax.set_title(title or f"{y} over {x}")
    ax.set_xlabel(x)
    ax.set_ylabel(y)

    if hue:
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    return fig


def plot_multi_time_series(
    df: pd.DataFrame,
    x: str,
    y_cols: List[str],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    normalize: bool = False,
) -> plt.Figure:
    """
    Plot multiple time series on same axes.

    Args:
        x: Time column
        y_cols: List of value columns
        normalize: Whether to normalize values (0-1 scale)
    """
    fig, ax = plt.subplots(figsize=figsize)

    for col in y_cols:
        values = df[col]
        if normalize:
            values = (values - values.min()) / (values.max() - values.min())
        ax.plot(df[x], values, label=col, marker="o", markersize=3)

    ax.set_title(title or "Time Series Comparison")
    ax.set_xlabel(x)
    ax.set_ylabel("Value" + (" (normalized)" if normalize else ""))
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    return fig


def plot_trends_by_group(
    df: pd.DataFrame,
    x: str,
    y: str,
    group: str,
    groups_to_show: Optional[List[str]] = None,
    agg_func: str = "mean",
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
) -> plt.Figure:
    """
    Plot aggregated trends by group.

    Args:
        x: Time column
        y: Value column
        group: Grouping column
        groups_to_show: Specific groups to include (default: all)
        agg_func: Aggregation function ('mean', 'sum', 'median')
    """
    fig, ax = plt.subplots(figsize=figsize)

    agg_df = df.groupby([x, group])[y].agg(agg_func).reset_index()

    if groups_to_show:
        agg_df = agg_df[agg_df[group].isin(groups_to_show)]

    sns.lineplot(data=agg_df, x=x, y=y, hue=group, marker="o", ax=ax)

    ax.set_title(title or f"{agg_func.title()} {y} by {group}")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    return fig


# =============================================================================
# Missing Data Plots
# =============================================================================


def plot_missing_heatmap(
    df: pd.DataFrame,
    title: str = "Missing Data Pattern",
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Plot heatmap showing missing data patterns.

    Rows are samples, columns are variables.
    White = missing, colored = present.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Create missing indicator matrix
    missing = df.isna().astype(int)

    # If too many rows, sample
    if len(missing) > 500:
        missing = missing.sample(500, random_state=42).sort_index()

    sns.heatmap(
        missing.T,
        cbar=False,
        cmap=["#2ecc71", "#e74c3c"],  # Green = present, Red = missing
        ax=ax,
        yticklabels=True,
    )

    ax.set_title(title)
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Variable")

    plt.tight_layout()
    return fig


def plot_missing_bar(
    df: pd.DataFrame,
    title: str = "Missing Values by Column",
    figsize: Tuple[int, int] = (12, 6),
    top_n: Optional[int] = None,
) -> plt.Figure:
    """
    Plot bar chart of missing percentage per column.

    Args:
        top_n: Show only top N columns with most missing (optional)
    """
    fig, ax = plt.subplots(figsize=figsize)

    missing_pct = (df.isna().sum() / len(df) * 100).sort_values(ascending=True)

    # Filter to columns with some missing
    missing_pct = missing_pct[missing_pct > 0]

    if top_n:
        missing_pct = missing_pct.tail(top_n)

    missing_pct.plot(kind="barh", ax=ax, color="coral")

    ax.set_title(title)
    ax.set_xlabel("Missing %")
    ax.set_ylabel("")
    ax.axvline(x=50, color="red", linestyle="--", alpha=0.7, label="50% threshold")
    ax.legend()

    # Add percentage labels
    for i, v in enumerate(missing_pct):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    return fig


def plot_missing_by_year(
    df: pd.DataFrame,
    year_col: str = "year",
    title: str = "Missing Data by Year",
    figsize: Tuple[int, int] = (12, 6),
) -> plt.Figure:
    """Plot total missing values per year."""
    fig, ax = plt.subplots(figsize=figsize)

    missing_by_year = df.groupby(year_col).apply(lambda x: x.isna().sum().sum())

    missing_by_year.plot(kind="bar", ax=ax, color="coral")

    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Missing Values")
    plt.xticks(rotation=45)

    plt.tight_layout()
    return fig


# =============================================================================
# Outlier Plots
# =============================================================================


def plot_boxplot_with_outliers(
    df: pd.DataFrame,
    col: str,
    label_col: Optional[str] = None,
    n_labels: int = 5,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """
    Plot boxplot with labeled outliers.

    Args:
        col: Numeric column to plot
        label_col: Column to use for outlier labels (e.g., 'country')
        n_labels: Number of outliers to label
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.boxplot(data=df, y=col, ax=ax)

    # Find outliers using IQR
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[(df[col] < lower) | (df[col] > upper)]

    if label_col and len(outliers) > 0:
        # Label extreme outliers
        extreme = outliers.nlargest(n_labels, col)
        for _, row in extreme.iterrows():
            ax.annotate(
                row[label_col],
                xy=(0, row[col]),
                xytext=(0.1, row[col]),
                fontsize=8,
                alpha=0.8,
            )

    ax.set_title(title or f"Boxplot of {col} with Outliers")
    ax.set_ylabel(col)

    plt.tight_layout()
    return fig


def plot_outliers_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    outlier_mask: pd.Series,
    label_col: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
) -> plt.Figure:
    """
    Plot scatter with outliers highlighted.

    Args:
        outlier_mask: Boolean Series indicating outliers
        label_col: Column to use for labels
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot non-outliers
    normal = df[~outlier_mask]
    ax.scatter(normal[x], normal[y], alpha=0.5, label="Normal", c="blue")

    # Plot outliers
    outliers = df[outlier_mask]
    ax.scatter(outliers[x], outliers[y], alpha=0.8, label="Outliers", c="red", s=100)

    # Label outliers
    if label_col:
        for _, row in outliers.iterrows():
            ax.annotate(
                row[label_col],
                xy=(row[x], row[y]),
                fontsize=8,
                alpha=0.7,
                xytext=(5, 5),
                textcoords="offset points",
            )

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title or f"Outliers: {y} vs {x}")
    ax.legend()

    plt.tight_layout()
    return fig


# =============================================================================
# Categorical Plots
# =============================================================================


def plot_countplot(
    df: pd.DataFrame,
    col: str,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    top_n: Optional[int] = None,
    horizontal: bool = False,
) -> plt.Figure:
    """
    Plot count of categories.

    Args:
        col: Categorical column
        top_n: Show only top N categories
        horizontal: Plot horizontally
    """
    fig, ax = plt.subplots(figsize=figsize)

    data = df.copy()
    if top_n:
        top_cats = data[col].value_counts().head(top_n).index
        data = data[data[col].isin(top_cats)]

    if horizontal:
        order = data[col].value_counts().index
        sns.countplot(data=data, y=col, order=order, ax=ax)
    else:
        order = data[col].value_counts().index
        sns.countplot(data=data, x=col, order=order, ax=ax)
        plt.xticks(rotation=45, ha="right")

    ax.set_title(title or f"Count of {col}")

    plt.tight_layout()
    return fig


def plot_barplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    ci: Optional[int] = None,
) -> plt.Figure:
    """
    Plot bar chart with mean values.

    Args:
        x: Categorical column
        y: Numeric column
        ci: Confidence interval (None to hide)
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.barplot(data=df, x=x, y=y, ci=ci, ax=ax)
    plt.xticks(rotation=45, ha="right")

    ax.set_title(title or f"Mean {y} by {x}")

    plt.tight_layout()
    return fig


# =============================================================================
# Initialize style on import
# =============================================================================

setup_plotting_style()
