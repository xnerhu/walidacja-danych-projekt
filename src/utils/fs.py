# src/utils/fs.py
"""
File system utilities for reading/writing various formats.
"""

import json
import os
from pathlib import Path
import pickle
from .json import json_stringify
from .array import as_array
import shutil
import numpy as np
from typing import Optional, List
import glob


# =============================================================================
# Pickle
# =============================================================================


def write_pickle(path: str, obj):
    """Write object to pickle file."""
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def read_pickle(path: str):
    """Read object from pickle file."""
    with open(path, "rb") as f:
        obj = pickle.load(f)
    return obj


# =============================================================================
# Text Files
# =============================================================================


def read_file(path: str, encoding="utf-8"):
    """Read text file."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def read_text(path: str, encoding="utf-8"):
    """Read text file (alias for read_file)."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_text(path: str, text: str, append: bool = False):
    """Write text to file."""
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        f.write(text)


# =============================================================================
# JSON
# =============================================================================


def write_json(path: str, obj, pretty: bool = False):
    """Write object to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        else:
            json.dump(obj, f, ensure_ascii=False)


def read_json(path: str):
    """Read JSON file."""
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def write_jsonl(path: str, items: list, append: bool = False):
    """Write items to JSON Lines file."""
    if not isinstance(items, list):
        items = [items]
    items = [json.dumps(item, ensure_ascii=False) for item in items]
    text = "\n".join(items) + "\n"
    write_text(path, text, append=append)


def read_jsonl(path: str) -> list:
    """Read JSON Lines file."""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


# =============================================================================
# NumPy
# =============================================================================


def write_numpy(path: str, arr: np.ndarray):
    """Write NumPy array to file."""
    with open(path, "wb") as f:
        np.save(f, arr)


def read_numpy(path: str, mode: str = "r") -> np.ndarray:
    """Read NumPy array from file."""
    return np.load(path, mmap_mode=mode)


# =============================================================================
# Parquet (NEW)
# =============================================================================


def write_parquet(
    df,  # pd.DataFrame
    path: str,
    compression: str = "snappy",
    index: bool = False,
):
    """
    Write DataFrame to Parquet file.

    Args:
        df: pandas DataFrame
        path: Output path
        compression: Compression codec ('snappy', 'gzip', 'brotli', None)
        index: Whether to include index
    """
    import pandas as pd

    ensure_parent_dir(path)
    df.to_parquet(path, compression=compression, index=index)


def read_parquet(
    path: str,
    columns: Optional[List[str]] = None,
):
    """
    Read Parquet file to DataFrame.

    Args:
        path: Input path
        columns: List of columns to read (None = all)

    Returns:
        pandas DataFrame
    """
    import pandas as pd

    return pd.read_parquet(path, columns=columns)


# =============================================================================
# CSV (NEW)
# =============================================================================


def write_csv(
    df,  # pd.DataFrame
    path: str,
    index: bool = False,
    encoding: str = "utf-8",
):
    """Write DataFrame to CSV file."""
    import pandas as pd

    ensure_parent_dir(path)
    df.to_csv(path, index=index, encoding=encoding)


def read_csv(
    path: str,
    encoding: str = "utf-8",
    **kwargs,
):
    """Read CSV file to DataFrame."""
    import pandas as pd

    return pd.read_csv(path, encoding=encoding, **kwargs)


# =============================================================================
# Binary
# =============================================================================


def write_bytes(path: str, data: bytes):
    """Write bytes to file."""
    with open(path, "wb") as f:
        f.write(data)


def read_bytes(path: str) -> bytes:
    """Read bytes from file."""
    with open(path, "rb") as f:
        return f.read()


# =============================================================================
# Directory Operations
# =============================================================================


def create_dir(paths):
    """Create directory(ies) if they don't exist."""
    paths = as_array(paths)
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def ensure_dir(path: str):
    """Ensure directory exists (alias for create_dir)."""
    Path(path).mkdir(parents=True, exist_ok=True)


def ensure_parent_dir(path: str):
    """Ensure parent directory of a file path exists."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def delete_path(path: str):
    """Delete file or directory."""
    path = Path(path)
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        Path.unlink(path)
        return
    shutil.rmtree(path, True)


def rimraf(path: str):
    """Recursively delete path (like rm -rf)."""
    path = Path(path)
    if not path.exists():
        return
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        raise ValueError(f"Path {path} is neither a file nor a directory.")


def copy_file(src: str, dst: str):
    """Copy file from src to dst."""
    ensure_parent_dir(dst)
    shutil.copy2(src, dst)


def move_file(src: str, dst: str):
    """Move file from src to dst."""
    ensure_parent_dir(dst)
    shutil.move(src, dst)


# =============================================================================
# File Listing (NEW)
# =============================================================================


def list_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = False,
) -> List[str]:
    """
    List files in directory matching pattern.

    Args:
        directory: Directory path
        pattern: Glob pattern (e.g., "*.csv", "*.parquet")
        recursive: Whether to search recursively

    Returns:
        List of file paths
    """
    if recursive:
        return sorted(glob.glob(os.path.join(directory, "**", pattern), recursive=True))
    else:
        return sorted(glob.glob(os.path.join(directory, pattern)))


def list_dirs(directory: str) -> List[str]:
    """List subdirectories in directory."""
    path = Path(directory)
    return sorted([str(d) for d in path.iterdir() if d.is_dir()])


def file_exists(path: str) -> bool:
    """Check if file exists."""
    return os.path.isfile(path)


def dir_exists(path: str) -> bool:
    """Check if directory exists."""
    return os.path.isdir(path)


def path_exists(path: str) -> bool:
    """Check if path exists (file or directory)."""
    return os.path.exists(path)


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(path)


def get_file_size_mb(path: str) -> float:
    """Get file size in megabytes."""
    return os.path.getsize(path) / (1024 * 1024)


# =============================================================================
# Path Utilities
# =============================================================================


def fs_safe_path(path: str) -> str:
    """Make path safe for file system (remove/replace unsafe characters)."""
    unsafe_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    safe_path = path
    for char in unsafe_chars:
        safe_path = safe_path.replace(char, "_")
    return safe_path


def get_extension(path: str) -> str:
    """Get file extension (without dot)."""
    return Path(path).suffix.lstrip(".")


def change_extension(path: str, new_ext: str) -> str:
    """Change file extension."""
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return str(Path(path).with_suffix(new_ext))


def get_filename(path: str, with_extension: bool = True) -> str:
    """Get filename from path."""
    if with_extension:
        return Path(path).name
    return Path(path).stem


def join_path(*parts) -> str:
    """Join path parts."""
    return os.path.join(*parts)
