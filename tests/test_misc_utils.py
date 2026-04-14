"""Tests for misc utility functions (plugins/misc/utils.py)."""
import pytest
from unittest.mock import MagicMock, patch


class TestSearchGifs:
    def test_calls_api_with_query(self):
        from plugins.misc.utils import search_gifs

        mock_api = MagicMock()
        mock_api.gifs_search_get.return_value = MagicMock()

        with patch("plugins.misc.utils.api_instance", mock_api):
            search_gifs("happy")

        mock_api.gifs_search_get.assert_called_once()
        call_args = mock_api.gifs_search_get.call_args[0]
        assert "happy" in call_args

    def test_returns_api_result_on_success(self):
        from plugins.misc.utils import search_gifs

        expected = MagicMock()
        mock_api = MagicMock()
        mock_api.gifs_search_get.return_value = expected

        with patch("plugins.misc.utils.api_instance", mock_api):
            result = search_gifs("cats")

        assert result == expected

    def test_returns_string_on_api_exception(self):
        """On API error, returns an error string instead of raising an exception."""
        import giphy_client
        from plugins.misc.utils import search_gifs

        mock_api = MagicMock()
        mock_api.gifs_search_get.side_effect = giphy_client.rest.ApiException()

        with patch("plugins.misc.utils.api_instance", mock_api):
            result = search_gifs("test")

        assert isinstance(result, str)

    def test_uses_limit_25(self):
        from plugins.misc.utils import search_gifs

        mock_api = MagicMock()
        mock_api.gifs_search_get.return_value = MagicMock()

        with patch("plugins.misc.utils.api_instance", mock_api):
            search_gifs("test")

        _, kwargs = mock_api.gifs_search_get.call_args
        assert kwargs.get("limit") == 25 or mock_api.gifs_search_get.call_args[0][2] == 25


class TestGifResponse:
    def test_returns_url_string(self):
        from plugins.misc.utils import gif_response

        mock_gif = MagicMock()
        mock_gif.url = "https://media.giphy.com/test.gif"

        mock_gifs_result = MagicMock()
        mock_gifs_result.data = [mock_gif]

        with patch("plugins.misc.utils.search_gifs", return_value=mock_gifs_result):
            result = gif_response("happy")

        assert result == "https://media.giphy.com/test.gif"

    def test_picks_from_available_gifs(self):
        from plugins.misc.utils import gif_response

        mock_gifs = [MagicMock() for _ in range(5)]
        for i, g in enumerate(mock_gifs):
            g.url = f"https://giphy.com/{i}.gif"

        mock_result = MagicMock()
        mock_result.data = mock_gifs

        with patch("plugins.misc.utils.search_gifs", return_value=mock_result):
            result = gif_response("test")

        assert result in [g.url for g in mock_gifs]
