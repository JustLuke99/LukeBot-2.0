"""Tests for the permission system (bot/permissions.py)."""
import pytest
from unittest.mock import MagicMock

from bot.constants import ROLES
from bot.permissions import Permissions, Roles

ADMIN_ID = ROLES["admin"][0]
MODERATOR_ID = ROLES["moderator"][0]
GIRL_ROLE_ID = ROLES["girls"][0]
RANDOM_ID = 999999999999


def _make_member(role_ids: list[int]) -> MagicMock:
    """Creates a mock discord.Member with the given role IDs."""
    member = MagicMock()
    member.roles = [MagicMock(id=rid) for rid in role_ids]
    return member


class TestPermissions:
    def test_admin_has_plugin_manager(self):
        assert Permissions.has_permission("plugin_manager", ADMIN_ID) is True

    def test_random_user_has_no_plugin_manager(self):
        assert Permissions.has_permission("plugin_manager", RANDOM_ID) is False

    def test_admin_can_turn_off(self):
        assert Permissions.has_permission("turn_off", ADMIN_ID) is True

    def test_random_cannot_turn_off(self):
        assert Permissions.has_permission("turn_off", RANDOM_ID) is False

    def test_admin_can_send_messages(self):
        assert Permissions.has_permission("send_messages", ADMIN_ID) is True

    def test_random_cannot_send_messages(self):
        assert Permissions.has_permission("send_messages", RANDOM_ID) is False

    def test_invalid_permission_raises_key_error(self):
        with pytest.raises(KeyError):
            Permissions.has_permission("nonexistent_permission", ADMIN_ID)

    def test_moderator_has_no_plugin_manager(self):
        """Moderators do not have plugin management rights."""
        assert Permissions.has_permission("plugin_manager", MODERATOR_ID) is False

    def test_all_admins_have_all_permissions(self):
        for admin_id in ROLES["admin"]:
            assert Permissions.has_permission("plugin_manager", admin_id) is True
            assert Permissions.has_permission("turn_off", admin_id) is True
            assert Permissions.has_permission("send_messages", admin_id) is True


class TestRoles:
    def test_admin_has_admin_role(self):
        assert Roles.has_role("admin", ADMIN_ID) is True

    def test_random_has_no_admin_role(self):
        assert Roles.has_role("admin", RANDOM_ID) is False

    def test_nonexistent_role_returns_false(self):
        """Unknown role name returns False, not KeyError."""
        assert Roles.has_role("nonexistent_role", ADMIN_ID) is False

    def test_all_moderators_have_moderator_role(self):
        for mod_id in ROLES["moderator"]:
            assert Roles.has_role("moderator", mod_id) is True


class TestIsGirl:
    def test_member_with_girl_role_is_girl(self):
        """Member whose server roles include a configured girls role ID."""
        member = _make_member([GIRL_ROLE_ID])
        assert Roles.is_girl(member) is True

    def test_member_without_girl_role_is_not_girl(self):
        member = _make_member([RANDOM_ID])
        assert Roles.is_girl(member) is False

    def test_member_with_no_roles_is_not_girl(self):
        member = _make_member([])
        assert Roles.is_girl(member) is False

    def test_all_configured_girl_role_ids_match(self):
        """Every ID in ROLES['girls'] is recognised as a girl role."""
        for role_id in ROLES["girls"]:
            member = _make_member([role_id])
            assert Roles.is_girl(member) is True

    def test_member_with_mixed_roles(self):
        """Member with one girl role among other roles is still recognised."""
        member = _make_member([RANDOM_ID, GIRL_ROLE_ID, 11111])
        assert Roles.is_girl(member) is True

    def test_detection_uses_member_roles_not_user_id(self):
        """is_girl reads server roles from the Member object, not a hardcoded user ID list."""
        member = _make_member([GIRL_ROLE_ID])
        member.id = RANDOM_ID  # user ID is NOT in any hardcoded list
        assert Roles.is_girl(member) is True
