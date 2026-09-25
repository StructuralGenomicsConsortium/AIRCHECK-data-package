"""Public API for listing and loading AIRCHECK datasets."""

import logging
import tempfile
import warnings
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from .cache import cache_path
from .config import ColumnConfig, get_dataset_config, load_config
from .exceptions import DatasetNotFoundError
from .remote import download_file, get_signed_url

logger = logging.getLogger(__name__)

DEFAULT_PARTNER = "HitGen"
DEFAULT_DATASET = "WDR91"


class DataLoader:
    """Load one pre-configured AIRCHECK dataset into a pandas DataFrame.

    Datasets are downloaded once to a local cache directory and read from
    there on subsequent calls. Column selection is applied when reading the
    local Parquet file, so requesting a subset of columns is cheap.

    Args:
        partner_name: Name of the dataset provider (default ``"HitGen"``).
        dataset_name: Name of the dataset (default ``"WDR91"``).
        columns: Columns to load; ``None`` loads every column.
        show_progress: Show a download progress bar.
        cache_dir: Cache root. Defaults to ``$AIRCHECKDATA_CACHE_DIR`` or
            ``~/.cache/aircheckdata``.
        use_cache: If ``False``, download to a temporary directory and delete
            the file after reading.

    Raises:
        DatasetNotFoundError: If the partner or dataset is unknown.
        ValueError: If ``columns`` contains names not defined for the dataset.

    """

    def __init__(
        self,
        partner_name: str = DEFAULT_PARTNER,
        dataset_name: str = DEFAULT_DATASET,
        columns: list[str] | None = None,
        show_progress: bool = True,
        cache_dir: str | Path | None = None,
        use_cache: bool = True,
    ):
        """Validate the requested dataset and columns against the registry."""
        self.partner_name = partner_name
        self.dataset_name = dataset_name
        self.config = get_dataset_config(partner_name, dataset_name)
        self.columns = self._validate_columns(columns)
        self.show_progress = show_progress
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        self.use_cache = use_cache

    def _validate_columns(self, columns: list[str] | None) -> list[str] | None:
        if columns is None:
            return None
        known = {c["name"] for c in self.config["columns"]}
        unknown = [c for c in columns if c not in known]
        if unknown:
            raise ValueError(
                f"Unknown column(s) for {self.partner_name}/{self.dataset_name}: "
                f"{', '.join(unknown)}. Available: {', '.join(sorted(known))}"
            )
        return list(columns)

    @property
    def path(self) -> Path:
        """Location of the cached Parquet file for this dataset."""
        return cache_path(self.partner_name, self.dataset_name, self.cache_dir)

    def get_dataset_columns(self) -> list[ColumnConfig]:
        """Return the column definitions (``name`` and ``description``)."""
        return self.config["columns"]

    def list_available_partners(self) -> list[str]:
        """Return the names of all dataset providers."""
        return list_partners()

    def list_available_datasets(self) -> dict[str, str]:
        """Return ``{dataset_name: description}`` for this loader's partner."""
        return list_datasets(self.partner_name)

    def download(self, dest: Path | None = None) -> Path:
        """Download the dataset Parquet file to ``dest`` (default: cache path).

        Returns:
            The path of the downloaded file.

        """
        target = dest if dest is not None else self.path
        url = get_signed_url(self.partner_name, self.dataset_name)
        return download_file(
            url,
            target,
            show_progress=self.show_progress,
            description=f"{self.partner_name}/{self.dataset_name}",
        )

    def load(self) -> pd.DataFrame:
        """Load the dataset, downloading it first if it is not cached.

        Returns:
            The dataset as a pandas DataFrame.

        """
        if not self.use_cache:
            with tempfile.TemporaryDirectory(prefix="aircheckdata-") as tmp:
                path = self.download(Path(tmp) / self.path.name)
                return self._read(path)

        if self.path.exists():
            logger.info("Using cached dataset at %s", self.path)
        else:
            self.download()
        return self._read(self.path)

    def _read(self, path: Path) -> pd.DataFrame:
        logger.info("Reading %s (columns: %s)", path, self.columns or "all")
        table = pq.read_table(path, columns=self.columns, memory_map=True)
        df = table.to_pandas()
        logger.info("Loaded DataFrame with shape %s", df.shape)
        return df

    def load_dataset_from_signed_url(
        self,
        columns: list[str] | None = None,
        show_progress: bool | None = None,
    ) -> pd.DataFrame:
        """Deprecated alias for :meth:`load`; use ``load()`` instead."""
        warnings.warn(
            "DataLoader.load_dataset_from_signed_url() is deprecated; use load()",
            DeprecationWarning,
            stacklevel=2,
        )
        if columns is not None:
            self.columns = self._validate_columns(columns)
        if show_progress is not None:
            self.show_progress = show_progress
        return self.load()


def list_partners() -> list[str]:
    """Return the names of all dataset providers in the registry."""
    return list(load_config())


def list_datasets(partner_name: str = DEFAULT_PARTNER) -> dict[str, str]:
    """Return ``{dataset_name: description}`` for one partner.

    Args:
        partner_name: Name of the dataset provider.

    Raises:
        DatasetNotFoundError: If the partner is unknown.

    """
    registry = load_config()
    if partner_name not in registry:
        raise DatasetNotFoundError(
            f"Partner '{partner_name}' not found. "
            f"Available partners: {', '.join(registry)}"
        )
    return {name: cfg["description"] for name, cfg in registry[partner_name].items()}


def get_columns(
    partner_name: str = DEFAULT_PARTNER, dataset_name: str = DEFAULT_DATASET
) -> list[ColumnConfig]:
    """Return the column definitions (``name`` and ``description``) of a dataset.

    Raises:
        DatasetNotFoundError: If the partner or dataset is unknown.

    """
    return get_dataset_config(partner_name, dataset_name)["columns"]


def load_dataset(
    partner_name: str = DEFAULT_PARTNER,
    dataset_name: str = DEFAULT_DATASET,
    columns: list[str] | None = None,
    show_progress: bool = True,
    cache_dir: str | Path | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Load a pre-configured dataset into a pandas DataFrame.

    The file is downloaded once into the local cache and re-read from there
    afterwards. See :class:`DataLoader` for parameter details.

    Raises:
        DatasetNotFoundError: If the partner or dataset is unknown.
        ValueError: If ``columns`` contains unknown column names.
        DownloadError: If the dataset cannot be downloaded.

    """
    return DataLoader(
        partner_name=partner_name,
        dataset_name=dataset_name,
        columns=columns,
        show_progress=show_progress,
        cache_dir=cache_dir,
        use_cache=use_cache,
    ).load()
