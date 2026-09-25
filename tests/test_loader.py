"""Tests for DataLoader / load_dataset with the network layer faked."""

from pathlib import Path

import pandas as pd
import pytest

from aircheckdata import DataLoader, clear_cache, load_dataset
from aircheckdata.cache import cache_path

pytestmark = pytest.mark.usefixtures("cache_dir")


def test_load_downloads_then_uses_cache(fake_remote, cache_dir: Path):
    df = load_dataset(
        "HitGen", "WDR91", columns=["ECFP4", "LABEL"], show_progress=False
    )
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["ECFP4", "LABEL"]
    assert len(df) == 3
    assert fake_remote.call_count == 1
    assert cache_path("HitGen", "WDR91").exists()
    assert cache_path("HitGen", "WDR91").is_relative_to(cache_dir)

    df2 = load_dataset("HitGen", "WDR91")  # all columns, from cache
    assert fake_remote.call_count == 1
    assert set(df2.columns) == {"SMILES", "ECFP4", "LABEL"}


def test_explicit_cache_dir_overrides_env(fake_remote, tmp_path: Path):
    custom = tmp_path / "elsewhere"
    load_dataset("HitGen", "WDR91", cache_dir=custom, show_progress=False)
    assert cache_path("HitGen", "WDR91", custom).exists()
    assert not cache_path("HitGen", "WDR91").exists()


def test_use_cache_false_leaves_nothing_behind(fake_remote):
    df = load_dataset("HitGen", "WDR91", use_cache=False, show_progress=False)
    assert len(df) == 3
    assert fake_remote.call_count == 1
    assert not cache_path("HitGen", "WDR91").exists()
    # A second call has to download again.
    load_dataset("HitGen", "WDR91", use_cache=False, show_progress=False)
    assert fake_remote.call_count == 2


def test_unknown_column_is_rejected_before_download(fake_remote):
    with pytest.raises(ValueError, match="Unknown column"):
        load_dataset("HitGen", "WDR91", columns=["ECFP4", "NOT_A_COLUMN"])
    assert fake_remote.call_count == 0


def test_dataset_names_with_special_characters_get_safe_paths():
    path = cache_path("HitGen", "Human PLCZ1 (D202R OR H170A&H215A)", Path("/c"))
    assert path == Path("/c/HitGen/Human_PLCZ1_D202R_OR_H170A_H215A.parquet")


def test_clear_cache(fake_remote):
    load_dataset("HitGen", "WDR91", show_progress=False)
    load_dataset("HitGen", "WDR12", show_progress=False)
    assert clear_cache("HitGen", "WDR91") == 1
    assert not cache_path("HitGen", "WDR91").exists()
    assert cache_path("HitGen", "WDR12").exists()
    assert clear_cache() == 1
    assert clear_cache() == 0
    with pytest.raises(ValueError, match="requires partner_name"):
        clear_cache(dataset_name="WDR91")


def test_dataloader_helpers(fake_remote):
    loader = DataLoader("HitGen", "WDR91", columns=["LABEL"], show_progress=False)
    assert "HitGen" in loader.list_available_partners()
    assert "WDR91" in loader.list_available_datasets()
    assert "LABEL" in [c["name"] for c in loader.get_dataset_columns()]
    assert list(loader.load().columns) == ["LABEL"]


def test_deprecated_alias_still_works(fake_remote):
    loader = DataLoader("HitGen", "WDR91", show_progress=False)
    with pytest.warns(DeprecationWarning, match="use load\\(\\)"):
        df = loader.load_dataset_from_signed_url(columns=["SMILES"])
    assert list(df.columns) == ["SMILES"]
