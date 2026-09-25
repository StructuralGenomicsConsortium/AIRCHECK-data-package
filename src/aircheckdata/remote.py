"""HTTP access to the AIRCHECK signed-URL service and dataset downloads."""

import logging
import os
from pathlib import Path

import requests
from tqdm import tqdm

from .exceptions import DownloadError

logger = logging.getLogger(__name__)

SIGNED_URL_ENDPOINT = (
    "https://fastapi-gcs-app-153945772792.northamerica-northeast2.run.app"
    "/generate-signed-url"
)
DEFAULT_TIMEOUT: tuple[float, float] = (10.0, 120.0)
"""(connect, read) timeout in seconds used for every HTTP request."""
CHUNK_SIZE = 1024 * 1024


def get_signed_url(
    partner_name: str,
    dataset_name: str,
    *,
    session: requests.Session | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
) -> str:
    """Ask the AIRCHECK service for a short-lived signed URL to a dataset.

    Args:
        partner_name: Name of the dataset provider.
        dataset_name: Name of the dataset.
        session: Optional ``requests.Session`` (useful for tests / connection reuse).
        timeout: ``(connect, read)`` timeout in seconds.

    Returns:
        A signed HTTPS URL.

    Raises:
        DownloadError: If the request fails or the response is malformed.

    """
    http = session or requests
    payload = {"company_name": partner_name, "target": dataset_name}
    try:
        response = http.post(SIGNED_URL_ENDPOINT, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise DownloadError(f"Could not reach signed-URL service: {exc}") from exc

    if response.status_code != 200:
        raise DownloadError(
            f"Signed-URL service returned {response.status_code} for "
            f"{partner_name}/{dataset_name}: {response.text[:200]}"
        )
    try:
        return response.json()["signed_url"]
    except (ValueError, KeyError, TypeError) as exc:
        raise DownloadError("Signed-URL service returned an unexpected body") from exc


def download_file(
    url: str,
    dest: Path,
    *,
    show_progress: bool = True,
    session: requests.Session | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
    description: str = "Downloading",
) -> Path:
    """Stream ``url`` to ``dest`` atomically.

    Data is written to ``<dest>.part`` and renamed into place only once the
    download completes, so an interrupted download never leaves a truncated
    file at ``dest``.

    Args:
        url: URL to download.
        dest: Destination file path; parent directories are created.
        show_progress: Show a ``tqdm`` progress bar.
        session: Optional ``requests.Session``.
        timeout: ``(connect, read)`` timeout in seconds.
        description: Label for the progress bar.

    Returns:
        ``dest``.

    Raises:
        DownloadError: If the request fails or returns a non-200 status.

    """
    http = session or requests
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    try:
        with http.get(url, stream=True, timeout=timeout) as response:
            if response.status_code != 200:
                raise DownloadError(
                    f"Download failed with status {response.status_code}: "
                    f"{response.text[:200]}"
                )
            total = int(response.headers.get("Content-Length", 0)) or None
            logger.info("Downloading %s (%s bytes)", dest.name, total or "unknown")
            with (
                open(part, "wb") as fh,
                tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=description,
                    disable=not show_progress,
                ) as bar,
            ):
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    fh.write(chunk)
                    bar.update(len(chunk))
        os.replace(part, dest)
    except requests.RequestException as exc:
        raise DownloadError(f"Download failed: {exc}") from exc
    finally:
        if part.exists():
            part.unlink()
    return dest
