# app/repositories/templates.py
from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

import numpy as np

DB_DIR = Path("db")
TEMPLATES_PATH = DB_DIR / "templates.npz"
META_PATH = DB_DIR / "templates.json"

_lock = Lock()
_cache: dict[str, np.ndarray] | None = None
_cache_mtime: float | None = None


def load_templates() -> dict[str, np.ndarray]:
    """
    Loads templates from disk with a small in-process cache.
    Cache is invalidated when templates.npz or templates.json changes.
    """
    global _cache, _cache_mtime

    if not TEMPLATES_PATH.exists() or not META_PATH.exists():
        return {}

    mtime = max(TEMPLATES_PATH.stat().st_mtime, META_PATH.stat().st_mtime)

    with _lock:
        if _cache is not None and _cache_mtime == mtime:
            return _cache

        names: list[str] = json.loads(META_PATH.read_text(encoding="utf-8"))
        data = np.load(TEMPLATES_PATH)

        _cache = {n: data[n].astype(np.float32) for n in names}
        _cache_mtime = mtime
        return _cache


def upsert_template(name: str, template: np.ndarray) -> None:
    """
    Inserts or updates a template and persists it.
    Also refreshes the in-process cache.
    """
    global _cache, _cache_mtime

    DB_DIR.mkdir(exist_ok=True)

    templates = load_templates()
    templates[name] = template.astype(np.float32)

    names = sorted(templates.keys())
    META_PATH.write_text(json.dumps(names, ensure_ascii=False, indent=2), encoding="utf-8")
    np.savez_compressed(TEMPLATES_PATH, **{n: templates[n] for n in names})

    # Refresh cache immediately (so identify sees it without waiting for mtime check)
    with _lock:
        _cache = templates
        _cache_mtime = max(TEMPLATES_PATH.stat().st_mtime, META_PATH.stat().st_mtime)
