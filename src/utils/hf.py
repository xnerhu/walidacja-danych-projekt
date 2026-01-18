import datasets as hf_datasets
from typing import Optional, Sequence, List, Dict
import sqlite3
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def load_hf_dataset(name: str, *args, label=None, **kwargs):
    label = label or name
    print(f"Loading {label}...")
    dataset = hf_datasets.load_dataset(name, *args, **kwargs)
    return dataset, label


def huggingface_from_sqlite(
    sqlite_path: str,
    out_dir: str,
    *,
    table: Optional[str] = None,
    columns: Optional[Sequence[str]] = None,
    computed_columns: Optional[Dict[str, str]] = None,
    where: Optional[str] = None,
    limit: Optional[int] = None,
    chunk_size: int = 250_000,
    parquet_suffix: str = "_parquet",
    overwrite: bool = False,
    pb: bool = True,
    estimate_total: bool = True,
) -> hf_datasets.Dataset:
    """
    Generic: SQLite -> Parquet shards -> HuggingFace Dataset -> save_to_disk cache.

    Behavior:
    - If out_dir exists and overwrite=False: loads from disk and returns.
    - If table is None:
        * if exactly one table exists -> uses it
        * else raises (forces caller to specify, avoiding wrong assumptions)

    computed_columns:
        dict of {alias: sql_expression}, appended to SELECT list.
        Example: {"DISCOVERY_DATE_ISO": "date(DISCOVERY_DATE)"}.

        If alias matches an existing column name, SQLite will return both columns unless
        you exclude the original from `columns`. (Explicit is better than magic.)

    Progress:
    - By default shows a progress bar with rows exported (no total).
    - If estimate_total=True, runs COUNT(*) (with WHERE if provided) to show % progress.
      This can be slow on large tables, so it's optional.
    """
    out_path = Path(out_dir)

    if out_path.exists() and not overwrite:
        return hf_datasets.load_from_disk(str(out_path))

    out_path.parent.mkdir(parents=True, exist_ok=True)

    parquet_dir = out_path.parent / f"{out_path.name}{parquet_suffix}"
    parquet_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(sqlite_path)
    try:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
            conn,
        )["name"].tolist()

        if not tables:
            raise RuntimeError(f"No tables found in SQLite database: {sqlite_path}")

        if table is None:
            if len(tables) == 1:
                table = tables[0]
            else:
                raise ValueError(
                    "SQLite database has multiple tables. "
                    f"Please specify `table=`. Available: {tables}"
                )

        if table not in tables:
            raise ValueError(f"Table '{table}' not found. Available: {tables}")

        info = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
        existing_cols = info["name"].tolist()
        existing_set = set(existing_cols)

        # Determine base columns
        if columns is None:
            base_cols = existing_cols  # preserve table order
        else:
            missing = [c for c in columns if c not in existing_set]
            if missing:
                raise ValueError(
                    f"Requested columns not found in table '{table}': {missing}. "
                    f"Available columns: {existing_cols}"
                )
            base_cols = list(columns)

        select_exprs: List[str] = []
        select_exprs.extend(base_cols)

        if computed_columns:
            for alias, expr in computed_columns.items():
                select_exprs.append(f"{expr} AS {alias}")

        query = f"SELECT {', '.join(select_exprs)} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if limit is not None:
            query += f" LIMIT {int(limit)}"

        # If small sample, just materialize quickly
        if limit is not None and limit <= chunk_size:
            df = pd.read_sql_query(query, conn)
            ds = hf_datasets.Dataset.from_pandas(df, preserve_index=False)

            if out_path.exists():
                if overwrite:
                    import shutil

                    shutil.rmtree(out_path, ignore_errors=True)
                else:
                    raise FileExistsError(f"Output already exists: {out_dir}")

            ds.save_to_disk(str(out_path))
            return ds

        # Optional total rows for % progress (can be expensive)
        total_rows = None
        if pb and estimate_total:
            count_q = f"SELECT COUNT(*) AS n FROM {table}"
            if where:
                count_q += f" WHERE {where}"
            total_rows = int(pd.read_sql_query(count_q, conn)["n"].iloc[0])

        shard_files: List[str] = []
        shard_idx = 0

        pbar = None
        if pb:
            pbar = tqdm(
                total=total_rows,
                unit="rows",
                desc=f"Exporting {table} -> parquet",
                dynamic_ncols=True,
            )

        try:
            for chunk_df in pd.read_sql_query(query, conn, chunksize=int(chunk_size)):
                shard_path = parquet_dir / f"part_{shard_idx:04d}.parquet"
                chunk_df.to_parquet(shard_path, index=False)
                shard_files.append(str(shard_path))
                shard_idx += 1

                if pbar is not None:
                    pbar.update(len(chunk_df))
        finally:
            if pbar is not None:
                pbar.close()

        if not shard_files:
            raise RuntimeError("Query returned no rows; nothing exported.")

    finally:
        conn.close()

    ds = hf_datasets.load_dataset(
        "parquet", data_files=sorted(shard_files), split="train"
    )

    if out_path.exists():
        if overwrite:
            import shutil

            shutil.rmtree(out_path, ignore_errors=True)
        else:
            raise FileExistsError(f"Output already exists: {out_dir}")

    ds.save_to_disk(str(out_path))
    return ds
