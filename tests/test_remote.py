"""Tests for the signed-URL request and the atomic file download."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from aircheckdata import DownloadError
from aircheckdata.remote import SIGNED_URL_ENDPOINT, download_file, get_signed_url
from tests.conftest import make_response


def test_get_signed_url_posts_partner_and_dataset():
    session = MagicMock()
    session.post.return_value = make_response(
        200, json_body={"signed_url": "https://x"}
    )
    assert get_signed_url("HitGen", "WDR91", session=session) == "https://x"
    session.post.assert_called_once()
    args, kwargs = session.post.call_args
    assert args == (SIGNED_URL_ENDPOINT,)
    assert kwargs["json"] == {"company_name": "HitGen", "target": "WDR91"}
    assert kwargs["timeout"]


@pytest.mark.parametrize(
    ("response", "fragment"),
    [
        (make_response(404, body=b"not found"), "returned 404"),
        (make_response(200, json_body={"oops": 1}), "unexpected body"),
        (make_response(200, body=b"<html>"), "unexpected body"),
    ],
)
def test_get_signed_url_failures(response, fragment):
    session = MagicMock()
    session.post.return_value = response
    with pytest.raises(DownloadError, match=fragment):
        get_signed_url("HitGen", "WDR91", session=session)


def test_get_signed_url_network_error():
    session = MagicMock()
    session.post.side_effect = requests.ConnectionError("down")
    with pytest.raises(DownloadError, match="Could not reach"):
        get_signed_url("HitGen", "WDR91", session=session)


def test_download_file_streams_to_destination(tmp_path: Path):
    body = b"x" * (3 * 1024 * 1024 + 7)
    session = MagicMock()
    session.get.return_value = make_response(200, body=body)
    dest = tmp_path / "nested" / "file.parquet"
    assert (
        download_file("https://x", dest, session=session, show_progress=False) == dest
    )
    assert dest.read_bytes() == body
    assert not dest.with_name("file.parquet.part").exists()


def test_download_file_bad_status_leaves_no_files(tmp_path: Path):
    session = MagicMock()
    session.get.return_value = make_response(403, body=b"expired")
    dest = tmp_path / "file.parquet"
    with pytest.raises(DownloadError, match="status 403"):
        download_file("https://x", dest, session=session, show_progress=False)
    assert not dest.exists()
    assert not dest.with_name("file.parquet.part").exists()


def test_download_file_interrupted_stream_leaves_no_files(tmp_path: Path):
    response = make_response(200, body=b"abc")

    def broken(chunk_size):
        yield b"a"
        raise requests.ConnectionError("reset")

    response.iter_content = broken
    session = MagicMock()
    session.get.return_value = response
    dest = tmp_path / "file.parquet"
    with pytest.raises(DownloadError, match="Download failed"):
        download_file("https://x", dest, session=session, show_progress=False)
    assert not dest.exists()
    assert not dest.with_name("file.parquet.part").exists()
