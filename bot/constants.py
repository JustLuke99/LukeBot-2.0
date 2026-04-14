# TODO: move roles and permissions to database
ROLES = {
    # admin/moderator: Discord USER IDs — checked against ctx.author.id
    "admin": [
        336903134859362314,
    ],
    "moderator": [
        484864561231561868,
        789186123186165156,
    ],
    # girls: Discord SERVER ROLE IDs — checked against member.roles
    # Update these to the actual role IDs from your Discord server.
    "girls": [
        500280806313295874,
        480107461215256576,
        471778363007172608,
        424702755299655690,
    ],
}

PERMISSIONS = {
    "plugin_manager": ["admin"],
    "send_messages": ["admin"],
    "turn_off": ["admin"],
}

PLUGIN_DIRECTORY = "plugins"


class ErrMessages:
    BAD_PERMISSIONS = "Na tuhle funkci nemáš oprávnění."


# Backward compat alias (original typo preserved for compatibility)
ErrMesagges = ErrMessages
