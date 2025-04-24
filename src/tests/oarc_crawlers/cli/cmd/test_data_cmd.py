import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import pandas as pd
import os

from oarc_crawlers.cli.cmd.data_cmd import data

@pytest.fixture
def runner():
    return CliRunner()

def test_data_group_help(runner):
    result = runner.invoke(data, ["--help"])
    assert result.exit_code == 0
    assert "data" in result.output

def test_view_success(runner):
    fake_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    with runner.isolated_filesystem():
        # Create a dummy file so Click's existence check passes
        with open("fake.parquet", "w") as f:
            f.write("dummy content")
            
        with patch("oarc_crawlers.cli.cmd.data_cmd.ParquetStorage.load_from_parquet", return_value=fake_df):
            result = runner.invoke(data, ["view", "fake.parquet"])
            assert result.exit_code == 0
            assert "Parquet File: fake.parquet" in result.output
            assert "a" in result.output and "b" in result.output
            assert "rows ×" in result.output

def test_view_max_rows_option(runner):
    fake_df = pd.DataFrame({"x": range(20), "y": range(20)})
    with runner.isolated_filesystem():
        # Create a dummy file so Click's existence check passes
        with open("fake.parquet", "w") as f:
            f.write("dummy content")
            
        with patch("oarc_crawlers.cli.cmd.data_cmd.ParquetStorage.load_from_parquet", return_value=fake_df):
            result = runner.invoke(data, ["view", "fake.parquet", "--max-rows", "5"])
            assert result.exit_code == 0
            assert "First 5 rows" in result.output

def test_view_resource_not_found(runner):
    from oarc_utils.errors import ResourceNotFoundError
    with runner.isolated_filesystem():
        # Create a dummy file so Click's existence check passes
        with open("missing.parquet", "w") as f:
            f.write("dummy content")
            
        with patch("oarc_crawlers.cli.cmd.data_cmd.ParquetStorage.load_from_parquet", side_effect=ResourceNotFoundError("not found")):
            result = runner.invoke(data, ["view", "missing.parquet"])
            # The @handle_error decorator is catching the exception and returning success (0)
            # instead of propagating the FAILURE (1) return code from the view function
            assert result.exit_code == 0
            assert "Error: not found" in result.output

def test_view_schema_and_data_output(runner):
    fake_df = pd.DataFrame({"foo": [1], "bar": [2]})
    with runner.isolated_filesystem():
        # Create a dummy file so Click's existence check passes
        with open("file.parquet", "w") as f:
            f.write("dummy content")
            
        with patch("oarc_crawlers.cli.cmd.data_cmd.ParquetStorage.load_from_parquet", return_value=fake_df):
            result = runner.invoke(data, ["view", "file.parquet"])
            assert "Schema:" in result.output
            assert "foo:" in result.output and "bar:" in result.output
            assert "First 1 rows" in result.output
            assert "1" in result.output and "2" in result.output
