"""Loading of the bundled dataset registry (``configs/datasets.yaml``)."""

from functools import lru_cache
from importlib import resources
from typing import TypedDict

import yaml

from .exceptions import DatasetNotFoundError

CONFIG_FILE = "datasets.yaml"


class ColumnConfig(TypedDict):
    """A single column entry in the registry."""

    name: str
    description: str


class DatasetConfig(TypedDict):
    """A single dataset entry in the registry."""

    description: str
    columns: list[ColumnConfig]


Registry = dict[str, dict[str, DatasetConfig]]
"""Mapping of ``partner -> dataset -> DatasetConfig``."""


@lru_cache(maxsize=1)
def load_config() -> Registry:
    """Load the dataset registry shipped inside the package.

    The result is cached for the lifetime of the process.

    Returns:
        Mapping of partner name to dataset name to dataset configuration.

    """
    path = resources.files(__package__).joinpath("configs", CONFIG_FILE)
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_dataset_config(partner_name: str, dataset_name: str) -> DatasetConfig:
    """Return the registry entry for one dataset.

    Args:
        partner_name: Name of the dataset provider (e.g. ``"HitGen"``).
        dataset_name: Name of the dataset (e.g. ``"WDR91"``).

    Returns:
        The dataset configuration.

    Raises:
        DatasetNotFoundError: If the partner or dataset is not in the registry.

    """
    registry = load_config()
    if partner_name not in registry:
        raise DatasetNotFoundError(
            f"Partner '{partner_name}' not found. "
            f"Available partners: {', '.join(registry)}"
        )
    datasets = registry[partner_name]
    if dataset_name not in datasets:
        raise DatasetNotFoundError(
            f"Dataset '{dataset_name}' not found for partner '{partner_name}'. "
            f"Available datasets: {', '.join(datasets)}"
        )
    return datasets[dataset_name]
