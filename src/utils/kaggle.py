from typing import Optional
from pathlib import Path


def find_sqlite_file(root: str) -> str:
    root_path = Path(root)
    candidates = list(root_path.rglob("*.sqlite")) + list(root_path.rglob("*.db"))
    if not candidates:
        raise FileNotFoundError(
            f"No .sqlite/.db file found under downloaded path: {root}"
        )
    candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
    return str(candidates[0])
