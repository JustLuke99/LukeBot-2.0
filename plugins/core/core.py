import logging

import discord
from decouple import config
from discord.ext import commands

from bot.constants import ErrMessages
from bot.permissions import Permissions
from bot.plugin_loader import all_plugins

logger = logging.getLogger(__name__)
__version__ = "2.0"


def setup(bot):
    bot.add_cog(Core(bot))


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_guilds = [
            int(x) for x in config("DISCORD_SERVER_IDS").replace(" ", "").split(",")
        ]
        logger.info(f"Initializing core module (version {__version__})")

    async def sync_commands_after_action(self):
        await self.bot.sync_commands(guild_ids=self.server_guilds)

    def _validate_plugin_name(self, plugin_name: str) -> bool:
        """Validates plugin name against the actual plugin list — prevents path traversal."""
        return plugin_name in all_plugins()

    @commands.slash_command(name="reload_plugin", description="Přenačte zadaný plugin.")
    async def reload_plugin(self, ctx, plugin_name: str):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMessages.BAD_PERMISSIONS)
            return

        if not self._validate_plugin_name(plugin_name):
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
            return

        try:
            self.bot.reload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je obnoven!")
        except discord.ExtensionNotLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except discord.ExtensionFailed as e:
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})")
        except Exception as e:
            logger.error(f"Error reloading plugin {plugin_name}: {e}")
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst. ({e})")

        await self.sync_commands_after_action()

    @commands.slash_command(name="activate_plugin", description="Aktivuje zadaný plugin.")
    async def activate_plugin(self, ctx, plugin_name: str):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMessages.BAD_PERMISSIONS)
            return

        if not self._validate_plugin_name(plugin_name):
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
            return

        try:
            self.bot.load_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je aktivován!")
        except discord.ExtensionAlreadyLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` je již aktivován!")
        except discord.ExtensionFailed as e:
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})")
        except Exception as e:
            logger.error(f"Error activating plugin {plugin_name}: {e}")
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze aktivovat. ({e})")

        await self.sync_commands_after_action()

    @commands.slash_command(name="deactivate_plugin", description="Deaktivuje zadaný plugin.")
    async def deactivate_plugin(self, ctx, plugin_name: str):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMessages.BAD_PERMISSIONS)
            return

        if not self._validate_plugin_name(plugin_name):
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
            return

        try:
            self.bot.unload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je deaktivován!")
        except discord.ExtensionNotLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except Exception as e:
            logger.error(f"Error deactivating plugin {plugin_name}: {e}")
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze deaktivovat. ({e})")

        await self.sync_commands_after_action()

    @commands.slash_command(name="show_all_plugins", description="Zobrazí názvy všech pluginů.")
    async def show_all_plugins(self, ctx):
        plugins = all_plugins()
        await ctx.respond(f"Dostupné pluginy: {', '.join(plugins)}")
