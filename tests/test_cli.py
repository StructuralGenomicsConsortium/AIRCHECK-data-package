"""Tests for the click CLI."""

import pytest
from click.testing import CliRunner

from aircheckdata.cli.main import cli

pytestmark = pytest.mark.usefixtures("cache_dir")


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "aircheckdata, version" in result.output


def test_partners_and_list(runner):
    assert "HitGen" in runner.invoke(cli, ["partners"]).output
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "WDR91:" in result.output
    assert runner.invoke(cli, ["list", "HitGen"]).output == result.output


def test_columns(runner):
    result = runner.invoke(cli, ["columns", "HitGen", "WDR91"])
    assert result.exit_code == 0
    assert "ECFP4:" in result.output


def test_columns_unknown_dataset_exits_1(runner):
    result = runner.invoke(cli, ["columns", "HitGen", "Nope"])
    assert result.exit_code == 1
    assert "Dataset 'Nope' not found" in result.output
    assert "wrap it in quotes" in result.output


def test_load(runner, fake_remote):
    result = runner.invoke(
        cli, ["load", "HitGen", "WDR91", "-c", "ECFP4, LABEL", "--no-progress"]
    )
    assert result.exit_code == 0, result.output
    assert "3 rows x 2 columns" in result.output
    assert fake_remote.call_count == 1


def test_load_unknown_column_exits_1(runner, fake_remote):
    result = runner.invoke(cli, ["load", "HitGen", "WDR91", "-c", "BOGUS"])
    assert result.exit_code == 1
    assert "Unknown column" in result.output


def test_cache_command(runner, cache_dir, fake_remote):
    assert str(cache_dir) in runner.invoke(cli, ["cache"]).output
    runner.invoke(cli, ["load", "--no-progress"])
    result = runner.invoke(cli, ["cache", "--clear"])
    assert result.exit_code == 0
    assert "Removed 1 cached file(s)" in result.output
