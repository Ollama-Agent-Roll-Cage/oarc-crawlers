import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock

import oarc_crawlers.cli.cmd.publish_cmd as publish_cmd

@pytest.fixture
def runner():
    return CliRunner()

def test_publish_group_help(runner):
    result = runner.invoke(publish_cmd.publish, ["--help"])
    assert result.exit_code == 0
    assert "publish" in result.output

def test_publish_pypi_success(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": True, "message": "done"}
        result = runner.invoke(publish_cmd.publish, ["pypi"])
        assert result.exit_code == 0
        assert "✓" in result.output

def test_publish_pypi_build_fail(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=False):
        result = runner.invoke(publish_cmd.publish, ["pypi"])
        assert result.exit_code != 0

def test_publish_pypi_publish_fail(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": False, "message": "fail"}
        result = runner.invoke(publish_cmd.publish, ["pypi"])
        assert result.exit_code != 0

def test_publish_pypi_test_flag(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": True, "message": "done"}
        result = runner.invoke(publish_cmd.publish, ["pypi", "--test"])
        assert result.exit_code == 0

def test_publish_pypi_no_build(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": True, "message": "done"}
        result = runner.invoke(publish_cmd.publish, ["pypi", "--no-build"])
        assert result.exit_code == 0

def test_publish_pypi_with_credentials(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": True, "message": "done"}
        result = runner.invoke(publish_cmd.publish, ["pypi", "--username", "u", "--password", "p"])
        assert result.exit_code == 0

def test_publish_pypi_with_config_file(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True), \
         patch("oarc_crawlers.utils.build_utils.BuildUtils.publish_package", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"success": True, "message": "done"}
        result = runner.invoke(publish_cmd.publish, ["pypi", "--config-file", "foo"])
        assert result.exit_code == 0
