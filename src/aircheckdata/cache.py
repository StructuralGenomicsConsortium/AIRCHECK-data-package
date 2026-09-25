"""Location and management of the on-disk dataset cache."""

import os
import re
from pathlib import Path

CACHE_DIR_ENV_VAR = "AIRCHECKDATA_CACHE_DIR"
"""Environment variable that overrides the default cache directory."""

_UNSAFE_CHARS = re.compile(r"[^\w.-]+")


def default_cache_dir() -> Path:
    """Return the cache directory.

    Resolution order: ``$AIRCHECKDATA_CACHE_DIR``, then
    ``$XDG_CACHE_HOME/aircheckdata``, then ``~/.cache/aircheckdata``.
    """
    override = os.environ.get(CACHE_DIR_ENV_VAR)
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "aircheckdata"


def _safe_name(name: str) -> str:
    return _UNSAFE_CHARS.sub("_", name).strip("_")


def cache_path(
    partner_name: str, dataset_name: str, cache_dir: Path | None = None
) -> Path:
    """Return the path where a dataset's Parquet file is cached.

    Args:
        partner_name: Name of the dataset provider.
        dataset_name: Name of the dataset.
        cache_dir: Cache root; defaults to :func:`default_cache_dir`.

    """
    root = cache_dir if cache_dir is not None else default_cache_dir()
    return root / _safe_name(partner_name) / f"{_safe_name(dataset_name)}.parquet"


def clear_cache(
    partner_name: str | None = None,
    dataset_name: str | None = None,
    cache_dir: Path | None = None,
) -> int:
    """Delete cached dataset files.

    Args:
        partner_name: Only clear datasets from this partner. ``None`` clears all.
        dataset_name: Only clear this dataset (requires ``partner_name``).
        cache_dir: Cache root; defaults to :func:`default_cache_dir`.

    Returns:
        Number of files removed.

    """
    root = cache_dir if cache_dir is not None else default_cache_dir()
    if dataset_name is not None:
        if partner_name is None:
            raise ValueError("dataset_name requires partner_name")
        targets = [cache_path(partner_name, dataset_name, root)]
    else:
        search_root = root / _safe_name(partner_name) if partner_name else root
        targets = list(search_root.rglob("*.parquet")) if search_root.exists() else []

    removed = 0
    for path in targets:
        if path.exists():
            path.unlink()
            removed += 1
    return removed
