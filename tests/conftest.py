"""Shared fixtures: an isolated cache dir and a fake remote that serves a tiny Parquet file."""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from aircheckdata import cache as cache_module
from aircheckdata import main as main_module

FRAME = pd.DataFrame(
    {
        "SMILES": ["C", "CC", "CCC"],
        "ECFP4": [[1, 0], [0, 1], [1, 1]],
        "LABEL": [0, 1, 1],
    }
)


@pytest.fixture
def parquet_bytes() -> bytes:
    sink = pa.BufferOutputStream()
    pq.write_table(pa.Table.from_pandas(FRAME), sink)
    return sink.getvalue().to_pybytes()


@pytest.fixture
def cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the default cache at a temp dir so tests never touch ~/.cache."""
    target = tmp_path / "cache"
    monkeypatch.setenv(cache_module.CACHE_DIR_ENV_VAR, str(target))
    return target


@pytest.fixture
def fake_remote(monkeypatch: pytest.MonkeyPatch, parquet_bytes: bytes) -> MagicMock:
    """Replace the network layer used by DataLoader.

    ``get_signed_url`` returns a fixed URL and ``download_file`` writes the
    test Parquet bytes to the requested destination. The returned mock records
    every download call so tests can assert on cache behaviour.
    """
    downloads = MagicMock(name="download_file")

    def _download(url: str, dest: Path, **kwargs) -> Path:
        downloads(url, dest, **kwargs)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(parquet_bytes)
        return dest

    monkeypatch.setattr(
        main_module, "get_signed_url", lambda p, d: f"https://signed/{p}/{d}"
    )
    monkeypatch.setattr(main_module, "download_file", _download)
    return downloads


def make_response(
    status: int = 200, body: bytes = b"", json_body=None, headers=None
) -> MagicMock:
    """Build a minimal stand-in for ``requests.Response``."""
    response = MagicMock(name=f"Response[{status}]")
    response.status_code = status
    response.text = body.decode(errors="replace") if body else ""
    response.headers = headers or {"Content-Length": str(len(body))}
    response.iter_content = lambda chunk_size: (
        body[i : i + chunk_size] for i in range(0, len(body), chunk_size)
    )
    if json_body is not None:
        response.json.return_value = json_body
    else:
        response.json.side_effect = ValueError("no json")
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response
