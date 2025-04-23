import pytest
from unittest.mock import patch, MagicMock

from oarc_crawlers.config.config_manager import ConfigManager

def test_config_manager_is_singleton():
    c1 = ConfigManager()
    c2 = ConfigManager()
    assert c1 is c2

def test_get_config_details():
    details = ConfigManager.get_config_details()
    assert isinstance(details, dict)
    assert "data_dir" in details

def test_get_current_config(monkeypatch):
    monkeypatch.setattr("oarc_crawlers.config.config.Config", MagicMock(DEFAULTS={"foo": "bar"}, get=lambda k: "baz"))
    cfg = ConfigManager.get_current_config()
    assert isinstance(cfg, dict)

def test_get_config_source(monkeypatch):
    monkeypatch.setattr("oarc_crawlers.config.config.Config", MagicMock(DEFAULTS={"foo": "bar"}, ENV_VARS={}, get=lambda k: "baz"))
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.find_config_file", lambda: None)
    assert isinstance(ConfigManager.get_config_source(), dict)

def test_create_config_file(tmp_path):
    config_path = tmp_path / "test.ini"
    assert ConfigManager.create_config_file(config_path, force=True) is True

def test_display_config_info(monkeypatch):
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.find_config_file", lambda: None)
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.get_current_config", lambda: {"foo": "bar"})
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.get_config_source", lambda: {"foo": "default"})
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.get_config_details", lambda: {"foo": {"description": "desc"}})
    ConfigManager.display_config_info()
