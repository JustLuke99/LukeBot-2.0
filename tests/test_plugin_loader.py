"""Tests for plugin discovery (bot/plugin_loader.py)."""
import os
from unittest.mock import patch

from bot.plugin_loader import all_plugins


class TestAllPlugins:
    def test_returns_list(self):
        result = all_plugins()
        assert isinstance(result, list)

    def test_contains_expected_plugins(self):
        result = all_plugins()
        expected = {"core", "reddit", "misc", "responses", "lunch"}
        assert expected.issubset(set(result)), f"Missing plugins: {expected - set(result)}"

    def test_filters_out_pycache(self):
        fake_dirs = ["core", "reddit", "__pycache__", "lunch"]

        def mock_isdir(path):
            name = os.path.basename(path)
            return name in fake_dirs

        with patch("os.listdir", return_value=fake_dirs):
            with patch("os.path.isdir", side_effect=mock_isdir):
                result = all_plugins()

        assert "__pycache__" not in result

    def test_filters_out_dunder_names(self):
        fake_dirs = ["core", "__init__", "__pycache__", "reddit"]

        with patch("os.listdir", return_value=fake_dirs):
            with patch("os.path.isdir", return_value=True):
                result = all_plugins()

        assert "__init__" not in result
        assert "__pycache__" not in result

    def test_returns_only_directories(self):
        """Files (non-directories) are ignored."""
        fake_entries = ["core", "reddit", "README.md", "utils.py"]

        def mock_isdir(path):
            name = os.path.basename(path)
            return name in ("core", "reddit")

        with patch("os.listdir", return_value=fake_entries):
            with patch("os.path.isdir", side_effect=mock_isdir):
                result = all_plugins()

        assert "README.md" not in result
        assert "utils.py" not in result
        assert "core" in result
        assert "reddit" in result

    def test_no_duplicates(self):
        result = all_plugins()
        assert len(result) == len(set(result)), "Duplicate plugin names in list"

    def test_plugin_names_are_strings(self):
        result = all_plugins()
        for plugin in result:
            assert isinstance(plugin, str)

    def test_path_traversal_not_possible(self):
        """all_plugins() should never return path traversal strings."""
        plugins = all_plugins()
        assert "../etc/passwd" not in plugins
        assert "../../secret" not in plugins
