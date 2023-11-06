import discord
from decouple import config
from discord.ext import commands

from abstract.constants import ErrMesagges
from abstract.permissions import Permissions
from abstract.cmds import all_plugins


__version__ = "2.0"


def setup(bot):
    bot.add_cog(Core(bot))


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.server_guilds = [
            int(x) for x in config("DISCORD_SERVER_IDS").replace(" ", "").split(",")
        ]
        print(f"Initializing core module (version {__version__})")

    async def sync_commands_after_action(self):
        await self.bot.sync_commands(guild_ids=self.server_guilds)

    # TODO dodělat choices
    @commands.slash_command(name="reload_plugin", description="Přenačte zadaný plugin.")
    async def reload_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)
            return

        try:
            self.bot.reload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je obnoven!")
        except discord.ExtensionNotFound:
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionNotLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except discord.ExtensionFailed:
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu!")
        except Exception as e:
            await ctx.respond(
                f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})"
            )

        await self.sync_commands_after_action()

    # TODO dodělat choices
    @commands.slash_command(
        name="activate_plugin", description="Aktivuje zadaný plugin."
    )
    async def activate_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.send(ErrMesagges.BAD_PERMISSIONS)
            return

        try:
            self.bot.load_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je aktivován!")
        except discord.ExtensionNotFound:
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionAlreadyLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` je již aktivován!")
        except discord.ExtensionFailed:
            await ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu!")
        except Exception as e:
            await ctx.respond(
                f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})"
            )
        await self.sync_commands_after_action()

    # TODO dodělat choices
    @commands.slash_command(
        name="deactivate_plugin", description="Deaktivuje zadaný plugin."
    )
    async def deactivate_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)
            return

        try:
            self.bot.unload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await ctx.respond(f"Plugin ``{plugin_name}`` je deaktivován!")
        except discord.ExtensionNotFound:
            await ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionNotLoaded:
            await ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except Exception as e:
            await ctx.respond(
                f"Plugin ``{plugin_name}`` nelze deaktivovat, obsahuje chybu! ({e})"
            )
        await self.sync_commands_after_action()

    @commands.slash_command(
        name="show_all_plugins", description="Zobrazí názvy všech pluginů."
    )
    async def show_all_plugins(self, ctx):
        await ctx.respond(all_plugins())
