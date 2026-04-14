"""Tests for lunch parsers (plugins/lunch/parsers/)."""
import pytest
from unittest.mock import MagicMock, patch

KNOFLIK_HTML = """
<table id="dmenu-small">
    <tr>
        <td><strong>1.</strong> Svíčková na smetaně</td>
        <td class="mright">130 Kč</td>
    </tr>
    <tr>
        <td><strong>2.</strong> Řízek s brambory</td>
        <td class="mright">110 Kč</td>
    </tr>
</table>
"""

ZLATALOD_HTML = """
<table class="menu-one-day">
    <tr><th>Polévka</th><th></th></tr>
    <tr><td>gulášová</td><td>40 kč</td></tr>
    <tr><td>svíčková</td><td>130 kč</td></tr>
    <tr><td>Dezert</td><td></td></tr>
    <tr><td>zmrzlina</td><td>30 kč</td></tr>
</table>
"""


def _make_mock_response(html: str, status: int = 200):
    mock = MagicMock()
    mock.status_code = status
    mock.content = html.encode("utf-8")
    return mock


class TestKnoflikParser:
    def test_returns_list(self):
        from plugins.lunch.parsers.knoflik import knoflik_parser

        with patch("requests.get", return_value=_make_mock_response(KNOFLIK_HTML)):
            result = knoflik_parser()

        assert isinstance(result, list)

    def test_returns_two_items(self):
        from plugins.lunch.parsers.knoflik import knoflik_parser

        with patch("requests.get", return_value=_make_mock_response(KNOFLIK_HTML)):
            result = knoflik_parser()

        assert len(result) == 2

    def test_raises_on_non_200(self):
        from plugins.lunch.parsers.knoflik import knoflik_parser

        with patch("requests.get", return_value=_make_mock_response("", status=404)):
            with pytest.raises(RuntimeError):
                knoflik_parser()

    def test_uses_timeout(self):
        from plugins.lunch.parsers.knoflik import knoflik_parser

        with patch("requests.get", return_value=_make_mock_response("", status=404)) as mock_get:
            try:
                knoflik_parser()
            except RuntimeError:
                pass

        _, kwargs = mock_get.call_args
        assert "timeout" in kwargs, "requests.get must be called with a timeout"

    def test_items_contain_price(self):
        from plugins.lunch.parsers.knoflik import knoflik_parser

        with patch("requests.get", return_value=_make_mock_response(KNOFLIK_HTML)):
            result = knoflik_parser()

        assert any("Kč" in item for item in result)


class TestZlatalodParser:
    def test_returns_list(self):
        from plugins.lunch.parsers.zlatalod import zlatalod_parser

        with patch("requests.get", return_value=_make_mock_response(ZLATALOD_HTML)):
            result = zlatalod_parser()

        assert isinstance(result, list)

    def test_stops_at_dezert(self):
        """Parser should ignore items after Dezert."""
        from plugins.lunch.parsers.zlatalod import zlatalod_parser

        with patch("requests.get", return_value=_make_mock_response(ZLATALOD_HTML)):
            result = zlatalod_parser()

        result_text = " ".join(result).lower()
        assert "zmrzlina" not in result_text

    def test_raises_on_non_200(self):
        from plugins.lunch.parsers.zlatalod import zlatalod_parser

        with patch("requests.get", return_value=_make_mock_response("", status=503)):
            with pytest.raises(RuntimeError):
                zlatalod_parser()

    def test_uses_timeout(self):
        from plugins.lunch.parsers.zlatalod import zlatalod_parser

        with patch("requests.get", return_value=_make_mock_response("", status=404)) as mock_get:
            try:
                zlatalod_parser()
            except RuntimeError:
                pass

        _, kwargs = mock_get.call_args
        assert "timeout" in kwargs

    def test_empty_table_returns_empty_list(self):
        from plugins.lunch.parsers.zlatalod import zlatalod_parser

        with patch("requests.get", return_value=_make_mock_response("<html></html>")):
            result = zlatalod_parser()

        assert result == []


class TestBudhaParser:
    def test_raises_on_non_200(self):
        from plugins.lunch.parsers.budha import budha_parser

        with patch("requests.get", return_value=_make_mock_response("", status=500)):
            with pytest.raises(RuntimeError):
                budha_parser()

    def test_uses_timeout(self):
        from plugins.lunch.parsers.budha import budha_parser

        with patch("requests.get", return_value=_make_mock_response("", status=404)) as mock_get:
            try:
                budha_parser()
            except RuntimeError:
                pass

        _, kwargs = mock_get.call_args
        assert "timeout" in kwargs

    def test_no_matching_date_returns_none_or_empty(self):
        """When today's date is not in the menu, parser returns None or empty list."""
        from plugins.lunch.parsers.budha import budha_parser

        html = "<html><h2>1. 1.</h2><p>Staré jídlo</p></html>"
        with patch("requests.get", return_value=_make_mock_response(html)):
            result = budha_parser()

        assert result is None or result == []


class TestRadegastParser:
    def test_raises_on_non_200(self):
        from plugins.lunch.parsers.radegast import radegast_parser

        with patch("requests.get", return_value=_make_mock_response("", status=503)):
            with pytest.raises(RuntimeError):
                radegast_parser()

    def test_uses_timeout(self):
        from plugins.lunch.parsers.radegast import radegast_parser

        with patch("requests.get", return_value=_make_mock_response("", status=404)) as mock_get:
            try:
                radegast_parser()
            except RuntimeError:
                pass

        _, kwargs = mock_get.call_args
        assert "timeout" in kwargs

    def test_returns_list(self):
        from plugins.lunch.parsers.radegast import radegast_parser

        html = "<html><strong>Pondělí 14. 4.</strong><span>Svíčková 130,-</span></html>"
        with patch("requests.get", return_value=_make_mock_response(html)):
            result = radegast_parser()

        assert isinstance(result, list)

    def test_always_appends_note(self):
        """Parser always appends a note about soups and specials."""
        from plugins.lunch.parsers.radegast import radegast_parser

        html = "<html><strong>Pondělí</strong></html>"
        with patch("requests.get", return_value=_make_mock_response(html)):
            result = radegast_parser()

        assert len(result) >= 1
        assert any("Bot je open" in item for item in result)
