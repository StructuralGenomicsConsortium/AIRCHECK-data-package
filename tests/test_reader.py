"""Unit tests for the DataLoader class and related dataset reading functionality."""

from unittest.mock import MagicMock, patch

from aircheckdata import DataLoader


def test_get_dataset_columns():
    """Test to ensure that the dataset columns can be retrieved correctly."""
    loader = DataLoader(partner_name="HitGen", dataset_name="WDR91")
    columns = loader.get_dataset_columns()
    assert isinstance(columns, list)
    assert "ECFP4" in [item["name"] for item in columns]
    assert "LABEL" in [item["name"] for item in columns]


@patch("aircheckdata.main.pq.read_table")
@patch("aircheckdata.main.gcsfs.GCSFileSystem")
def test_load_dataset_with_mocked_gcs(mock_gcsfs, mock_read_table):
    """Test loading a dataset with mocked GCS file system and parquet reading."""
    # Mock GCS file system and parquet loading
    mock_fs = MagicMock()
    mock_gcsfs.return_value = mock_fs
    mock_fs.info.return_value = {"size": 1024}
    mock_file = MagicMock()
    mock_file.read.side_effect = [b"data", b""]
    mock_fs.open.return_value.__enter__.return_value = mock_file

    mock_table = MagicMock()
    mock_df = MagicMock()
    mock_table.to_pandas.return_value = mock_df
    mock_read_table.return_value = mock_table

    loader = DataLoader(partner_name="HitGen", dataset_name="WDR91", columns=["ECFP4"])
    df = loader.load_dataset_from_signed_url(columns=["ECFP4"])
    assert df is not None
    mock_read_table.assert_called_once()
