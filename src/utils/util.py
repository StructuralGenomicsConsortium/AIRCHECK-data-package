"""Utility functions and classes for configuration loading and dataset access."""

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import requests
import yaml


@dataclass
class ConfigLoader:
    """A class to load configuration from a YAML file."""

    config_file: str = "./src/configs/datasets.yaml"

    def __post_init__(self):
        """Post-initialization checks for the config file."""
        if not self.config_file.endswith(".yaml"):
            raise ValueError("Only YAML files are supported.")

    def load(self, config_name="datasets.yaml") -> dict:
        """Load config from package root configs folder."""
        try:
            with (
                resources.files("aircheckdata")
                .parent.joinpath("configs", config_name)
                .open("r") as f
            ):
                return yaml.safe_load(f)
        except (AttributeError, FileNotFoundError):
            # Fallback: try to find it relative to the current file
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / "configs" / config_name
            with open(config_path, "r") as f:  # noqa: UP015
                return yaml.safe_load(f)


@dataclass
class GetDataset:
    """A class to get a signed URL for a dataset stored in Google Cloud Storage (GCS)."""

    provider_name: str
    dataset_name: str

    def get_dataset_path(self) -> str:
        """Construct the GCS path for the dataset."""
        payload = {
            "company_name": self.provider_name,
            "target": self.dataset_name,
        }

        try:
            response = requests.post(
                "https://fastapi-gcs-app-153945772792.northamerica-northeast2.run.app/generate-signed-url",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                signed_url = data["signed_url"]
                return signed_url

            else:
                print("Error:", response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            print("Request failed:", str(e))
