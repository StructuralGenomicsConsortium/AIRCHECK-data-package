"""aircheckdata: A Python package for loading datasets from Google Cloud Storage (GCS) using signed URLs."""

import io
import logging

import gcsfs
import pandas as pd
import pyarrow.parquet as pq
import requests
from tqdm import tqdm

from utils.util import ConfigLoader, GetDataset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """A class to load datasets from Google Cloud Storage (GCS) using signed URLs."""

    def __init__(
        self,
        partner_name: str,
        dataset_name: str,
        columns: list[str] | None = None,
        show_progress: bool = False,
    ):
        """Initialize the DataLoader with GCS URL and optional parameters.

        Args:
            partner_name (str): Name of the dataset provider.
            dataset_name (str): Name of the pre-configured dataset.
            columns (list[str] | None): Specific columns to load from the Parquet file.
            show_progress (bool): Whether to display a progress bar during download.

        """
        self.partner_name = partner_name
        self.dataset_name = dataset_name
        self.columns = columns
        self.show_progress = show_progress
        self.datasets = ConfigLoader().load()

    def get_dataset_columns(self) -> dict[str, str]:
        """Get information about available columns in a dataset.

        Returns:
            Dictionary mapping column names to their descriptions

        """
        if self.partner_name not in self.datasets:
            available = ", ".join(self.datasets.keys())
            raise ValueError(
                f"Partner '{self.partner_name}' not found. Available partners: {available}"
            )

        if self.dataset_name not in self.datasets[self.partner_name]:
            available = ", ".join(self.datasets.keys())
            raise ValueError(
                f"Dataset '{self.dataset_name}' not found. Available datasets: {available}"
            )

        return self.datasets[self.partner_name][self.dataset_name]["columns"]

    def list_available_partners(self) -> dict[str, str]:
        """List all available partners.

        Returns:
            Dictionary mapping partner names to their descriptions

        """
        # return {name for name in self.datasets.keys()}

        return set(self.datasets)

    def list_available_datasets(self) -> dict[str, str]:
        """List all available pre-configured datasets.

        Args:
            partner_name: Name of the pre-configured partner

        Returns:
            Dictionary mapping dataset names to their description

        """
        return {
            name: config["description"]
            for name, config in self.datasets[self.partner_name].items()
        }

    def load_dataset_from_signed_url(
        self,
        columns: list[str] | None,
        show_progress: bool = True,
    ) -> pd.DataFrame | None:
        """Read a Parquet file from a signed HTTPS GCS URL with a progress bar.

        Args:
            columns (Optional[List[str]]): Specific columns to load from the Parquet file.
            show_progress (bool): Whether to display a progress bar during download.

        Returns:
            Optional[pd.DataFrame]: Loaded DataFrame or None on failure.

        """
        try:
            logger.info("Reading dataset config...")
            signed_url = GetDataset(
                provider_name=self.partner_name, dataset_name=self.dataset_name
            ).get_dataset_path()

            logger.info("Downloading Parquet file...")

            if show_progress:
                with requests.get(signed_url, stream=True) as response:
                    print("response", response)
                    if response.status_code != 200:
                        raise ValueError(
                            f"Failed to download file from signed URL: {response.status_code} {response.text}"
                        )

                    response.raise_for_status()
                    total_size = int(response.headers.get("Content-Length", 0))
                    logger.info("File size: %.2f MB", total_size / (1024 * 1024))

                    buffer = io.BytesIO()
                    chunk_size = 1024 * 1024  # 1MB
                    with tqdm(
                        total=total_size, unit="B", unit_scale=True, desc="Downloading"
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                buffer.write(chunk)
                                pbar.update(len(chunk))

                    buffer.seek(0)
                    logger.info(
                        "Loading selected columns: %s",
                        columns if columns else "All Columns",
                    )
                    table = pq.read_table(buffer, columns=columns)
                    df = table.to_pandas()
            else:
                logger.info("Loading Parquet data into DataFrame...")
                df = pd.read_parquet(
                    signed_url,
                    engine="pyarrow",
                    storage_options={"token": "anon"},
                    columns=columns,
                )

            logger.info("DataFrame loaded successfully with shape: %s", df.shape)
            return df

        except Exception as e:
            logger.error("Failed to load dataset. Error: %s", str(e))
            return None


def load_dataset(
    partner_name: str = "HitGen",
    dataset_name: str = "WDR91",
    show_progress: bool = True,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Load a pre-configured dataset.

    Args:
        partner_name: Name of the dataset provider (default: "HitGen")
        dataset_name: Name of the pre-configured dataset
        columns: Specific columns to load (optional)
        show_progress: Whether to display a progress bar (default: True)

    Returns:
        pandas DataFrame containing the dataset

    """
    try:
        loader = DataLoader(
            partner_name=partner_name,
            dataset_name=dataset_name,
            columns=columns,
            show_progress=show_progress,
        )

        return loader.load_dataset_from_signed_url(
            columns=columns, show_progress=show_progress
        )
    except Exception as e:
        logger.error("Failed to load dataset '%s'. Error: %s", dataset_name, str(e))
        return None


def list_datasets(
    partner_name: str = "HitGen", dataset_name: str = "WDR91"
) -> dict[str, str]:
    """List all available pre-configured datasets.

    Args:
        partner_name: Name of the pre-configured partner
        dataset_name: Name of the pre-configured dataset

    Returns:
        Dictionary mapping dataset names to their descriptions

    """
    loader = DataLoader(partner_name=partner_name, dataset_name=dataset_name)
    return loader.list_available_datasets()


def get_columns(
    partner_name: str = "HitGen", dataset_name: str = "WDR91"
) -> dict[str, str]:
    """Get information about available columns in a dataset.

    Args:
        partner_name: Name of the dataset provider
        dataset_name: Name of the pre-configured dataset

    Returns:
        Dictionary mapping column names to their description

    """
    loader = DataLoader(partner_name=partner_name, dataset_name=dataset_name)
    return loader.get_dataset_columns()


def load_dataset_two(
    partner_name: str = "HitGen",
    dataset_name: str = "WDR91",
    show_progress: bool = True,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Load a pre-configured dataset.

    Args:
        partner_name: Name of the dataset provider (default: "HitGen")
        dataset_name: Name of the pre-configured dataset
        columns: Specific columns to load (optional)
        show_progress: Whether to display a progress bar (default: True)

    Returns:
        pandas DataFrame containing the dataset

    """
    try:
        loader = DataLoader(
            partner_name=partner_name,
            dataset_name=dataset_name,
            columns=columns,
            show_progress=show_progress,
        )

        return loader.load_dataset_from_signed_url(
            columns=columns, show_progress=show_progress
        )
    except Exception as e:
        logger.error("Failed to load dataset '%s'. Error: %s", dataset_name, str(e))
        return None
