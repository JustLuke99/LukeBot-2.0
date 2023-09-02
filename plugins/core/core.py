import discord
from discord.ext import commands

from abstract.constants import ErrMesagges
from abstract.permissions import Permissions
from .constants import PLUGINS

__version__ = "2.0"


def setup(bot):
    bot.add_cog(Core(bot))


class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(f"Initializing core module (version {__version__})")

    # TODO dodělat choices
    @commands.slash_command(name="reload_plugin", description="Přenačte zadaný plugin.")
    async def reload_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)

        try:
            self.bot.reload_extension(f"plugins.{plugin_name}")
        except discord.ExtensionNotFound:
            ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionNotLoaded:
            ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except discord.ExtensionFailed:
            ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu!")
        except Exception as e:
            ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})")

        await ctx.respond(f"Plugin ``{plugin_name}`` je obnoven!")

    # TODO dodělat choices
    @commands.slash_command(name="activate_plugin", description="Aktivuje zadaný plugin.")
    async def activate_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.send(ErrMesagges.BAD_PERMISSIONS)

        try:
            self.bot.load_extension(f"plugins.{plugin_name}")
        except discord.ExtensionNotFound:
            ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionAlreadyLoaded:
            ctx.respond(f"Plugin ``{plugin_name}`` je již aktivován!")
        except discord.ExtensionFailed:
            ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu!")
        except Exception as e:
            ctx.respond(f"Plugin ``{plugin_name}`` nelze načíst, obsahuje chybu! ({e})")

        await ctx.respond(f"Plugin ``{plugin_name}`` je aktivován!")

    # TODO dodělat choices
    @commands.slash_command(name="deactivate_plugin", description="Deaktivuje zadaný plugin.")
    async def deactivate_plugin(self, ctx, plugin_name):
        if not Permissions.has_permission("plugin_manager", ctx.author.id):
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)

        try:
            self.bot.unload_extension(f"plugins.{plugin_name}")
        except discord.ExtensionNotFound:
            ctx.respond(f"Plugin ``{plugin_name}`` neexistuje!")
        except discord.ExtensionNotLoaded:
            ctx.respond(f"Plugin ``{plugin_name}`` není aktivován!")
        except Exception as e:
            ctx.respond(f"Plugin ``{plugin_name}`` nelze deaktivovat, obsahuje chybu! ({e})")

        await ctx.respond(f"Plugin ``{plugin_name}`` je deaktivován!")

    @commands.slash_command(name="show_all_plugins", description="Zobrazí názvy všech pluginů.")
    async def show_all_plugins(self, ctx):
        await ctx.respond(PLUGINS)
