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

from .main import DataLoader, load_dataset, get_columns, list_datasets

__all__ = ["DataLoader", "load_dataset", "get_columns", "list_datasets"]
__version__ = "0.1.0"

# loader = DataLoader(
#     partner_name="HitGen", dataset_name="WDR91", columns=["ECFP4", "ECFP6"], show_progress=True)
# print("Available partners:", loader.list_available_partners())
# print("Available datasets:", loader.list_available_datasets())
# print("Dataset columns:", loader.get_dataset_columns())


# pip install --editable .
