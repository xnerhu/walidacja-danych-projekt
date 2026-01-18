import pandas as pd
import numpy as np
from typing import Optional, List, Union, Literal
import re


# =============================================================================
# DataFrame Information
# =============================================================================


def df_info(df: pd.DataFrame) -> dict:
    """
    Get comprehensive information about a DataFrame.

    Returns:
        dict with keys: rows, cols, dtypes, memory_mb, missing_total, missing_pct
    """
    return {
        "rows": len(df),
        "cols": len(df.columns),
        "dtypes": df.dtypes.value_counts().to_dict(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "missing_total": df.isna().sum().sum(),
        "missing_pct": round(df.isna().sum().sum() / df.size * 100, 2),
    }


def df_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of missing values per column.

    Returns:
        DataFrame with columns: column, missing_count, missing_pct, dtype
    """
    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    summary = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": missing.values,
            "missing_pct": missing_pct.values,
            "dtype": df.dtypes.values.astype(str),
        }
    )

    return summary.sort_values("missing_pct", ascending=False).reset_index(drop=True)


def df_describe_all(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extended describe for all column types (numeric + categorical).

    Returns:
        DataFrame with statistics for all columns
    """
    stats = []

    for col in df.columns:
        col_stats = {
            "column": col,
            "dtype": str(df[col].dtype),
            "non_null": df[col].notna().sum(),
            "null_count": df[col].isna().sum(),
            "null_pct": round(df[col].isna().sum() / len(df) * 100, 2),
            "unique": df[col].nunique(),
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update(
                {
                    "mean": df[col].mean(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "q25": df[col].quantile(0.25),
                    "median": df[col].median(),
                    "q75": df[col].quantile(0.75),
                    "max": df[col].max(),
                }
            )
        else:
            col_stats.update(
                {
                    "mean": None,
                    "std": None,
                    "min": None,
                    "q25": None,
                    "median": None,
                    "q75": None,
                    "max": None,
                    "top_value": (
                        df[col].value_counts().index[0]
                        if df[col].notna().any()
                        else None
                    ),
                    "top_freq": (
                        df[col].value_counts().iloc[0]
                        if df[col].notna().any()
                        else None
                    ),
                }
            )

        stats.append(col_stats)

    return pd.DataFrame(stats)


# =============================================================================
# Column Name Cleaning
# =============================================================================


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to snake_case.

    - Converts to lowercase
    - Replaces spaces, hyphens, dots with underscores
    - Removes special characters (parentheses, %, etc.)
    - Removes duplicate underscores
    """
    df = df.copy()

    def clean_name(name: str) -> str:
        # Convert to lowercase
        name = name.lower()
        # Replace common separators with underscore
        name = re.sub(r"[\s\-\.]+", "_", name)
        # Remove parentheses and their content or just the parentheses
        name = re.sub(r"\(([^)]*)\)", r"_\1", name)
        # Remove special characters except underscore
        name = re.sub(r"[^a-z0-9_]", "", name)
        # Remove duplicate underscores
        name = re.sub(r"_+", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        return name

    df.columns = [clean_name(col) for col in df.columns]
    return df


# =============================================================================
# Column Filtering
# =============================================================================


def drop_constant_columns(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Drop columns that have only one unique value (excluding NaN).
    """
    df = df.copy()
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]

    if verbose and constant_cols:
        print(f"Dropping {len(constant_cols)} constant columns: {constant_cols}")

    return df.drop(columns=constant_cols)


def drop_high_missing(
    df: pd.DataFrame, threshold: float = 0.5, verbose: bool = True
) -> pd.DataFrame:
    """
    Drop columns with missing percentage above threshold.

    Args:
        threshold: Maximum allowed missing percentage (0.0 to 1.0)
    """
    df = df.copy()
    missing_pct = df.isna().sum() / len(df)
    high_missing_cols = missing_pct[missing_pct > threshold].index.tolist()

    if verbose and high_missing_cols:
        print(
            f"Dropping {len(high_missing_cols)} columns with >{threshold*100}% missing: {high_missing_cols}"
        )

    return df.drop(columns=high_missing_cols)


def select_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return list of numeric column names."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def select_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Return list of categorical/object column names."""
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


# =============================================================================
# Type Conversion
# =============================================================================


def convert_numeric_columns(
    df: pd.DataFrame, columns: List[str], errors: str = "coerce"
) -> pd.DataFrame:
    """
    Convert specified columns to numeric type.

    Args:
        columns: List of column names to convert
        errors: 'coerce' (invalid -> NaN), 'ignore', or 'raise'
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors=errors)
    return df


def convert_to_datetime(
    df: pd.DataFrame, columns: List[str], format: Optional[str] = None
) -> pd.DataFrame:
    """Convert specified columns to datetime type."""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format=format, errors="coerce")
    return df


# =============================================================================
# Feature Engineering - Transformations
# =============================================================================


def add_log_column(
    df: pd.DataFrame, col: str, suffix: str = "_log", offset: float = 1.0
) -> pd.DataFrame:
    """
    Add log-transformed column.

    Args:
        col: Source column name
        suffix: Suffix for new column name
        offset: Value to add before log (to handle zeros)
    """
    df = df.copy()
    new_col = f"{col}{suffix}"
    df[new_col] = np.log(df[col] + offset)
    return df


def add_squared_column(df: pd.DataFrame, col: str, suffix: str = "_sq") -> pd.DataFrame:
    """Add squared column."""
    df = df.copy()
    new_col = f"{col}{suffix}"
    df[new_col] = df[col] ** 2
    return df


def add_pct_change(
    df: pd.DataFrame,
    col: str,
    group_by: Optional[str] = None,
    sort_by: Optional[str] = None,
    suffix: str = "_pct_change",
) -> pd.DataFrame:
    """
    Add percentage change column.

    Args:
        col: Source column
        group_by: Column to group by (e.g., 'country')
        sort_by: Column to sort by before calculating change (e.g., 'year')
    """
    df = df.copy()
    new_col = f"{col}{suffix}"

    if sort_by:
        df = df.sort_values(sort_by)

    if group_by:
        df[new_col] = df.groupby(group_by)[col].pct_change() * 100
    else:
        df[new_col] = df[col].pct_change() * 100

    return df


def add_diff(
    df: pd.DataFrame,
    col: str,
    group_by: Optional[str] = None,
    sort_by: Optional[str] = None,
    suffix: str = "_diff",
) -> pd.DataFrame:
    """
    Add difference (year-over-year change) column.

    Args:
        col: Source column
        group_by: Column to group by (e.g., 'country')
        sort_by: Column to sort by before calculating diff (e.g., 'year')
    """
    df = df.copy()
    new_col = f"{col}{suffix}"

    if sort_by:
        df = df.sort_values(sort_by)

    if group_by:
        df[new_col] = df.groupby(group_by)[col].diff()
    else:
        df[new_col] = df[col].diff()

    return df


def add_quantile_bins(
    df: pd.DataFrame,
    col: str,
    n_bins: int = 4,
    labels: Optional[List[str]] = None,
    suffix: str = "_bin",
) -> pd.DataFrame:
    """
    Add categorical column based on quantile binning.

    Args:
        col: Source column
        n_bins: Number of bins (default 4 for quartiles)
        labels: Custom labels (e.g., ['Low', 'Medium', 'High', 'Very High'])
    """
    df = df.copy()
    new_col = f"{col}{suffix}"

    if labels is None:
        labels = [f"Q{i+1}" for i in range(n_bins)]

    df[new_col] = pd.qcut(df[col], q=n_bins, labels=labels, duplicates="drop")
    return df


# =============================================================================
# Outlier Detection
# =============================================================================


def detect_outliers_iqr(df: pd.DataFrame, col: str, k: float = 1.5) -> pd.Series:
    """
    Detect outliers using IQR method.

    Args:
        col: Column to check
        k: IQR multiplier (default 1.5)

    Returns:
        Boolean Series (True = outlier)
    """
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr

    return (df[col] < lower_bound) | (df[col] > upper_bound)


def detect_outliers_zscore(
    df: pd.DataFrame, col: str, threshold: float = 3.0
) -> pd.Series:
    """
    Detect outliers using Z-score method.

    Args:
        col: Column to check
        threshold: Z-score threshold (default 3.0)

    Returns:
        Boolean Series (True = outlier)
    """
    z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
    return z_scores > threshold


def get_outlier_bounds_iqr(
    df: pd.DataFrame, col: str, k: float = 1.5
) -> tuple[float, float]:
    """Get IQR-based outlier bounds (lower, upper)."""
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    return (q1 - k * iqr, q3 + k * iqr)


def winsorize_column(
    df: pd.DataFrame, col: str, limits: tuple = (0.05, 0.95)
) -> pd.DataFrame:
    """
    Winsorize column by clipping to quantile limits.

    Args:
        col: Column to winsorize
        limits: (lower_quantile, upper_quantile)
    """
    df = df.copy()
    lower = df[col].quantile(limits[0])
    upper = df[col].quantile(limits[1])
    df[col] = df[col].clip(lower, upper)
    return df


# =============================================================================
# Imputation
# =============================================================================


def impute_by_group(
    df: pd.DataFrame,
    col: str,
    group_by: str,
    method: Literal["mean", "median", "mode"] = "median",
) -> pd.DataFrame:
    """
    Impute missing values using group statistics.

    Args:
        col: Column to impute
        group_by: Column to group by
        method: 'mean', 'median', or 'mode'
    """
    df = df.copy()

    if method == "mean":
        fill_values = df.groupby(group_by)[col].transform("mean")
    elif method == "median":
        fill_values = df.groupby(group_by)[col].transform("median")
    elif method == "mode":
        fill_values = df.groupby(group_by)[col].transform(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    df[col] = df[col].fillna(fill_values)
    return df


def impute_interpolate(
    df: pd.DataFrame,
    col: str,
    group_by: Optional[str] = None,
    method: str = "linear",
    sort_by: Optional[str] = None,
) -> pd.DataFrame:
    """
    Impute missing values using interpolation (for time series).

    Args:
        col: Column to impute
        group_by: Column to group by (e.g., 'country')
        method: Interpolation method ('linear', 'time', 'nearest', etc.)
        sort_by: Column to sort by before interpolation (e.g., 'year')
    """
    df = df.copy()

    if sort_by:
        df = df.sort_values([group_by, sort_by] if group_by else [sort_by])

    if group_by:
        df[col] = df.groupby(group_by)[col].transform(
            lambda x: x.interpolate(method=method)
        )
    else:
        df[col] = df[col].interpolate(method=method)

    return df


def impute_forward_backward(
    df: pd.DataFrame, col: str, group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Impute using forward fill then backward fill.
    Useful for time series edge cases.
    """
    df = df.copy()

    if group_by:
        df[col] = df.groupby(group_by)[col].transform(lambda x: x.ffill().bfill())
    else:
        df[col] = df[col].ffill().bfill()

    return df


# =============================================================================
# Correlation Analysis
# =============================================================================


def correlation_matrix(
    df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "pearson"
) -> pd.DataFrame:
    """
    Calculate correlation matrix for numeric columns.

    Args:
        columns: List of columns (default: all numeric)
        method: 'pearson', 'spearman', or 'kendall'
    """
    if columns is None:
        columns = select_numeric_columns(df)

    return df[columns].corr(method=method)


def top_correlations(
    df: pd.DataFrame, n: int = 20, method: str = "pearson"
) -> pd.DataFrame:
    """
    Get top N strongest correlations (excluding self-correlations).

    Returns:
        DataFrame with columns: var1, var2, correlation
    """
    corr = correlation_matrix(df, method=method)

    # Get upper triangle (excluding diagonal)
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

    # Stack and sort
    pairs = upper.stack().reset_index()
    pairs.columns = ["var1", "var2", "correlation"]
    pairs["abs_corr"] = pairs["correlation"].abs()

    return (
        pairs.sort_values("abs_corr", ascending=False)
        .head(n)
        .drop(columns=["abs_corr"])
        .reset_index(drop=True)
    )


# =============================================================================
# Aggregation Helpers
# =============================================================================


def summary_by_group(
    df: pd.DataFrame,
    group_col: str,
    agg_cols: List[str],
    agg_funcs: List[str] = ["mean", "std", "min", "max", "count"],
) -> pd.DataFrame:
    """
    Calculate summary statistics grouped by a column.

    Args:
        group_col: Column to group by
        agg_cols: Columns to aggregate
        agg_funcs: Aggregation functions
    """
    return df.groupby(group_col)[agg_cols].agg(agg_funcs).round(2)
