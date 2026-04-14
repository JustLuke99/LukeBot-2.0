import os

from bot.constants import PLUGIN_DIRECTORY

# Project root is the parent of the bot/ directory
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def all_plugins() -> list:
    """Returns a list of all available plugin names."""
    plugins_path = os.path.join(_ROOT_DIR, PLUGIN_DIRECTORY)

    plugins = []
    for name in os.listdir(plugins_path):
        if name.startswith("_"):
            continue
        if os.path.isdir(os.path.join(plugins_path, name)):
            plugins.append(name)

    return plugins
