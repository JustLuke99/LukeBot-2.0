"""Tests for the responses module (plugins/responses/)."""
from datetime import datetime, UTC, timedelta

import pytest


class TestDelayCheck:
    def setup_method(self):
        """Reset ZKRATKY tmp values before each test."""
        from plugins.responses.constants import ZKRATKY
        for key in ZKRATKY:
            ZKRATKY[key]["tmp"] = datetime.now(UTC) - timedelta(days=999)

    def test_returns_false_when_delay_passed(self):
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        ZKRATKY["gn"]["tmp"] = datetime.now(UTC) - timedelta(seconds=99999)
        result = delay_check("gn")
        assert result is False

    def test_returns_true_within_delay(self):
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        ZKRATKY["gn"]["tmp"] = datetime.now(UTC)
        result = delay_check("gn")
        assert result is True

    def test_updates_tmp_after_trigger(self):
        """tmp must be updated to the current time after a successful pass."""
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        ZKRATKY["gn"]["tmp"] = datetime.now(UTC) - timedelta(seconds=99999)
        delay_check("gn")

        delta = (datetime.now(UTC) - ZKRATKY["gn"]["tmp"]).total_seconds()
        assert delta < 1, "tmp must be updated to the current time"

    def test_does_not_update_tmp_when_blocked(self):
        """tmp must not change when the call is within the delay period."""
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        original_tmp = datetime.now(UTC) - timedelta(seconds=1)
        ZKRATKY["gn"]["tmp"] = original_tmp
        delay_check("gn")

        assert ZKRATKY["gn"]["tmp"] == original_tmp

    def test_zero_delay_never_blocks(self):
        """Keys with delay=0 should never block."""
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        ZKRATKY["hihahuhahi"]["tmp"] = datetime.now(UTC)
        result = delay_check("hihahuhahi")
        assert result is False

    def test_long_delay_key(self):
        from plugins.responses.utils import delay_check
        from plugins.responses.constants import ZKRATKY

        # fuchs has delay=86400 (1 day)
        ZKRATKY["fuchs"]["tmp"] = datetime.now(UTC) - timedelta(hours=1)
        result = delay_check("fuchs")
        assert result is True  # still within the delay period


class TestZkratky:
    def test_has_all_required_keys(self):
        from plugins.responses.constants import ZKRATKY

        required = {"gn", "gm", "stop", "badbot", "hihahuhahi", "okBot", "off"}
        for key in required:
            assert key in ZKRATKY, f"Missing key: {key}"

    def test_all_entries_have_required_fields(self):
        from plugins.responses.constants import ZKRATKY

        for key, value in ZKRATKY.items():
            assert "reg" in value, f"{key}: missing 'reg'"
            assert "delay" in value, f"{key}: missing 'delay'"
            assert "tmp" in value, f"{key}: missing 'tmp'"

    def test_all_regexes_are_compiled(self):
        from plugins.responses.constants import ZKRATKY

        for key, value in ZKRATKY.items():
            assert hasattr(value["reg"], "search"), f"{key}: 'reg' is not a compiled regex"

    def test_all_delays_are_non_negative(self):
        from plugins.responses.constants import ZKRATKY

        for key, value in ZKRATKY.items():
            assert value["delay"] >= 0, f"{key}: delay must not be negative"

    def test_gn_regex_matches_goodnight(self):
        from plugins.responses.constants import ZKRATKY

        assert ZKRATKY["gn"]["reg"].search("gn")
        assert ZKRATKY["gn"]["reg"].search("GN")
        assert ZKRATKY["gn"]["reg"].search("Ahoj gn lidi")

    def test_gn_regex_does_not_match_partial(self):
        from plugins.responses.constants import ZKRATKY

        assert not ZKRATKY["gn"]["reg"].search("gna")

    def test_gm_regex_matches_good_morning(self):
        from plugins.responses.constants import ZKRATKY

        assert ZKRATKY["gm"]["reg"].search("Dobré ráno")
        assert ZKRATKY["gm"]["reg"].search("Dobry ran")

    def test_stop_regex_matches(self):
        from plugins.responses.constants import ZKRATKY

        assert ZKRATKY["stop"]["reg"].search("krutý světe")

    def test_badbot_regex_matches(self):
        from plugins.responses.constants import ZKRATKY

        assert ZKRATKY["badbot"]["reg"].search("Co zas děláš")
