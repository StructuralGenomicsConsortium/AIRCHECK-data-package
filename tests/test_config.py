"""Tests for the bundled dataset registry."""

import pytest

from aircheckdata import DatasetNotFoundError, get_columns, list_datasets, list_partners
from aircheckdata.config import get_dataset_config, load_config


def test_registry_is_well_formed():
    registry = load_config()
    assert "HitGen" in registry
    for partner, datasets in registry.items():
        assert datasets, f"{partner} has no datasets"
        for name, cfg in datasets.items():
            assert cfg["description"], f"{partner}/{name} has no description"
            names = [c["name"] for c in cfg["columns"]]
            assert names, f"{partner}/{name} has no columns"
            assert len(names) == len(set(names)), f"{partner}/{name} has duplicates"


def test_list_partners_and_datasets():
    assert "HitGen" in list_partners()
    datasets = list_datasets("HitGen")
    assert "WDR91" in datasets
    assert datasets["WDR91"].startswith("WDR91")


def test_get_columns():
    names = [c["name"] for c in get_columns("HitGen", "WDR91")]
    assert {"ECFP4", "ECFP6", "LABEL", "SMILES"} <= set(names)
    assert get_columns() == get_columns("HitGen", "WDR91")


@pytest.mark.parametrize(
    ("partner", "dataset", "fragment"),
    [
        ("Nobody", "WDR91", "Partner 'Nobody' not found"),
        ("HitGen", "Nope", "Dataset 'Nope' not found for partner 'HitGen'"),
    ],
)
def test_unknown_partner_or_dataset(partner, dataset, fragment):
    with pytest.raises(DatasetNotFoundError, match=fragment):
        get_dataset_config(partner, dataset)
    with pytest.raises(
        ValueError, match=fragment
    ):  # DatasetNotFoundError is a ValueError
        get_columns(partner, dataset)


def test_list_datasets_unknown_partner():
    with pytest.raises(DatasetNotFoundError, match="Available partners"):
        list_datasets("Nobody")
