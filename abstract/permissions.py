from abstract.constants import PERMISSIONS, ROLES


class Permissions:
    @staticmethod
    def has_permission(permission_for: str, user_id: int) -> bool:
        for role in PERMISSIONS[permission_for]:
            if user_id in ROLES[role]:
                return True

        return False


class Roles:
    @staticmethod
    def is_girl(user_id: int) -> bool:
        for role in ROLES["girls"]:
            if user_id in ROLES[role]:
                return True

        return False

    @staticmethod
    def has_role(permission_for: str, user_id: int) -> bool:
        if user_id in ROLES[permission_for]:
            return True

        return False
