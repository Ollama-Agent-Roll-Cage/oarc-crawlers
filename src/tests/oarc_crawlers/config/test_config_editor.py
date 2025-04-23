import pytest
from unittest.mock import patch, MagicMock

from oarc_crawlers.config.config_editor import ConfigEditor

def test_config_editor_is_singleton():
    e1 = ConfigEditor()
    e2 = ConfigEditor()
    assert e1 is e2

def test_config_editor_ensure_initialized():
    # Should not raise
    ConfigEditor._ensure_initialized()

def test_config_editor_is_config_changed_false(monkeypatch):
    monkeypatch.setattr(ConfigEditor, "_current_config", {"foo": "bar"})
    monkeypatch.setattr(ConfigEditor, "_config_details", {"foo": {"description": ""}})
    with patch("oarc_crawlers.config.config_editor.Config", MagicMock(return_value=MagicMock(get=lambda k: "bar"))):
        assert ConfigEditor.is_config_changed() is False

def test_config_editor_reset_to_defaults(monkeypatch):
    # Simulate a config with two keys to ensure reset works for all keys
    monkeypatch.setattr(ConfigEditor, "_current_config", {"foo": "bar", "baz": "qux"})
    monkeypatch.setattr(ConfigEditor, "_config_details", {"foo": {"description": ""}, "baz": {"description": ""}})
    class DummyConfig:
        DEFAULTS = {"foo": "baz", "baz": "reset"}
    with patch("oarc_crawlers.config.config_editor.Config", DummyConfig):
        ConfigEditor.reset_to_defaults()
        assert ConfigEditor._current_config["foo"] == "baz"
        assert ConfigEditor._current_config["baz"] == "reset"

def test_config_editor_save_changes(monkeypatch, tmp_path):
    config_file = tmp_path / "test.ini"
    monkeypatch.setattr("oarc_crawlers.config.config_manager.ConfigManager.find_config_file", lambda: config_file)
    monkeypatch.setattr("oarc_crawlers.utils.paths.Paths.ensure_config_dir", lambda: tmp_path)
    edited = {"foo": "bar"}
    with patch("oarc_crawlers.config.config_editor.questionary.confirm", MagicMock(return_value=MagicMock(ask=lambda: False))):
        assert ConfigEditor.save_changes(edited) is True

def test_config_editor_confirm_reset():
    with patch("oarc_crawlers.config.config_editor.questionary.confirm", MagicMock(return_value=MagicMock(ask=lambda: True))):
        assert ConfigEditor.confirm_reset() is True
