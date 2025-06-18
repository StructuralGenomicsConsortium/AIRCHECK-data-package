"""aircheckdata - A lightweight data access library for loading and interacting with datasets stored on Google Cloud Storage (GCS).

Features:
    - Load datasets stored as Parquet files on GCS
    - Filter by dataset name or columns
    - Return Pandas DataFrames directly
    - Easily configurable for different environments

Usage:
    from aircheckdata import DataLoader
    loader = DataLoader(dataset_name="example", columns=["ECFP4"])
    df = loader.load_dataset()
"""

from .main import DataLoader, get_columns, list_datasets, load_dataset

__all__ = ["DataLoader", "load_dataset", "get_columns", "list_datasets"]
__version__ = "1.2.0"
