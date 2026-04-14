import discord

from bot.constants import PERMISSIONS, ROLES


class Permissions:
    @staticmethod
    def has_permission(permission_for: str, user_id: int) -> bool:
        for role in PERMISSIONS[permission_for]:
            if user_id in ROLES[role]:
                return True
        return False


class Roles:
    @staticmethod
    def is_girl(member: discord.Member) -> bool:
        """Returns True if the Discord member has any of the configured girls role IDs.

        ROLES["girls"] must contain Discord server role IDs (not user IDs).
        The check reads the member's actual server roles at call time.
        """
        member_role_ids = {role.id for role in member.roles}
        return bool(member_role_ids & set(ROLES["girls"]))

    @staticmethod
    def has_role(role_name: str, user_id: int) -> bool:
        return user_id in ROLES.get(role_name, [])
