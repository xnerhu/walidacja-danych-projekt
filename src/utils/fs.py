import json
import os
from pathlib import Path
import pickle
from .json import json_stringify
from .array import as_array
import shutil
import numpy as np


def write_pickle(path: str, obj):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def read_pickle(path: str):
    with open(path, "rb") as f:
        obj = pickle.load(f)
    return obj


def read_file(path: str, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_json(path: str, obj, pretty: bool = False):
    with open(path, "w") as f:
        if pretty:
            json.dump(obj, f, indent=2)
        else:
            json.dump(obj, f)


def read_json(path: str):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def write_numpy(path: str, arr: np.ndarray):
    with open(path, "wb") as f:
        np.save(f, arr)


def read_numpy(path: str, mode: str = "r") -> np.ndarray:
    return np.load(path, mmap_mode=mode)


def write_text(path: str, text: str, append: bool = False):
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        f.write(text)


def read_text(path: str, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def create_dir(paths):
    paths = as_array(paths)
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def write_jsonl(path: str, items: list, append: bool = False):
    if not isinstance(items, list):
        items = [items]
    items = [json.dumps(item) for item in items]
    text = "\n".join(items) + "\n"
    write_text(path, text, append=append)


def delete_path(path: str):
    path = Path(path)
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        Path.unlink(path)
        return
    shutil.rmtree(path, True)


def write_bytes(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def rimraf(path: str):
    path = Path(path)
    if not path.exists():
        return
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        raise ValueError(f"Path {path} is neither a file nor a directory.")


def fs_safe_path(path: str) -> str:
    unsafe_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    safe_path = path
    for char in unsafe_chars:
        safe_path = safe_path.replace(char, "_")
    return safe_path
