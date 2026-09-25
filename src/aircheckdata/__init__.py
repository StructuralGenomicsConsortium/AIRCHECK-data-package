"""aircheckdata - load AIRCHECK DEL datasets (Parquet files on GCS) into pandas.

Usage:
    from aircheckdata import load_dataset, list_datasets, get_columns

    list_datasets("HitGen")
    get_columns("HitGen", "WDR91")
    df = load_dataset("HitGen", "WDR91", columns=["ECFP4", "LABEL"])

Datasets are downloaded once into a local cache (``~/.cache/aircheckdata`` or
``$AIRCHECKDATA_CACHE_DIR``) and read from there on later calls.
"""

import logging

from .cache import CACHE_DIR_ENV_VAR, clear_cache, default_cache_dir
from .exceptions import AircheckDataError, DatasetNotFoundError, DownloadError
from .main import (
    DataLoader,
    get_columns,
    list_datasets,
    list_partners,
    load_dataset,
)

__version__ = "2.0.0"

__all__ = [
    "AircheckDataError",
    "CACHE_DIR_ENV_VAR",
    "DataLoader",
    "DatasetNotFoundError",
    "DownloadError",
    "__version__",
    "clear_cache",
    "default_cache_dir",
    "get_columns",
    "list_datasets",
    "list_partners",
    "load_dataset",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
