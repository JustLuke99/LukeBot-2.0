import logging
from typing import List

import discord
from decouple import config
from discord import app_commands
from discord.ext import commands

from abstract.constants import ErrMesagges
from abstract.permissions import Permissions
from abstract.cmds import all_plugins

logger = logging.getLogger(__name__)

__version__ = "2.6.4"


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Core(bot))


class Core(commands.Cog):
    """Core management commands for the bot, handling plugin lifecycle."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the Core cog.

        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        # Parsing guild IDs for targeted synchronization
        self.server_guilds = [
            discord.Object(id=int(x))
            for x in config("DISCORD_SERVER_IDS", default="").replace(" ", "").split(",")
            if x
        ]
        logger.info(f"Initializing core module (version {__version__})")

    async def _sync_commands(self) -> None:
        """Synchronizes commands with the configured guilds.

        This ensures that any changes to commands (loading/unloading plugins)
        are reflected in the Discord client immediately.
        """
        if not self.server_guilds:
            logger.warning("No guild IDs configured. Syncing globally.")
            await self.bot.tree.sync()
            return

        for guild_obj in self.server_guilds:
            try:
                # Copy global commands to the specific guild to ensure they update immediately
                self.bot.tree.copy_global_to(guild=guild_obj)
                await self.bot.tree.sync(guild=guild_obj)
                logger.info(f"Synced commands to guild {guild_obj.id}")
            except discord.HTTPException as e:
                logger.error(f"Failed to sync guild {guild_obj.id}: {e}")

    async def plugin_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocompletion function for plugin names.

        Args:
            interaction (discord.Interaction): The interaction context.
            current (str): The current user input.

        Returns:
            List[app_commands.Choice[str]]: A list of matching plugin names.
        """
        plugins = all_plugins()
        return [
            app_commands.Choice(name=plugin, value=plugin)
            for plugin in plugins
            if current.lower() in plugin.lower()
        ][:25]  # Discord limits choices to 25

    @app_commands.command(
        name="reload_plugin", description="Reloads a specified plugin."
    )
    @app_commands.autocomplete(plugin_name=plugin_autocomplete)
    async def reload_plugin(
        self, interaction: discord.Interaction, plugin_name: str
    ) -> None:
        """Reloads a bot extension (plugin).

        Args:
            interaction (discord.Interaction): The interaction object.
            plugin_name (str): The name of the plugin to reload.
        """
        if not Permissions.has_permission("plugin_manager", interaction.user.id):
            await interaction.response.send_message(
                ErrMesagges.BAD_PERMISSIONS, ephemeral=True
            )
            return

        # Deferring because reloading and syncing can take time
        await interaction.response.defer()

        try:
            await self.bot.reload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await self._sync_commands()
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` successfully reloaded!"
            )
        except discord.ExtensionNotFound:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` does not exist!", ephemeral=True
            )
        except discord.ExtensionNotLoaded:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` is not currently loaded!", ephemeral=True
            )
        except discord.ExtensionFailed as e:
            logger.error(f"Failed to reload {plugin_name}: {e}")
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` failed to load due to an error.",
                ephemeral=True,
            )
        except Exception as e:
            logger.exception(f"Unexpected error reloading {plugin_name}")
            await interaction.followup.send(
                f"An unexpected error occurred: {e}", ephemeral=True
            )

    @app_commands.command(
        name="activate_plugin", description="Activates (loads) a specified plugin."
    )
    @app_commands.autocomplete(plugin_name=plugin_autocomplete)
    async def activate_plugin(
        self, interaction: discord.Interaction, plugin_name: str
    ) -> None:
        """Loads a bot extension.

        Args:
            interaction (discord.Interaction): The interaction object.
            plugin_name (str): The name of the plugin to load.
        """
        if not Permissions.has_permission("plugin_manager", interaction.user.id):
            await interaction.response.send_message(
                ErrMesagges.BAD_PERMISSIONS, ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            await self.bot.load_extension(f"plugins.{plugin_name}.{plugin_name}")
            await self._sync_commands()
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` successfully activated!"
            )
        except discord.ExtensionNotFound:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` does not exist!", ephemeral=True
            )
        except discord.ExtensionAlreadyLoaded:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` is already active!", ephemeral=True
            )
        except discord.ExtensionFailed as e:
            logger.error(f"Failed to load {plugin_name}: {e}")
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` failed to load due to an error.",
                ephemeral=True,
            )
        except Exception as e:
            logger.exception(f"Unexpected error loading {plugin_name}")
            await interaction.followup.send(
                f"An unexpected error occurred: {e}", ephemeral=True
            )

    @app_commands.command(
        name="deactivate_plugin", description="Deactivates (unloads) a specified plugin."
    )
    @app_commands.autocomplete(plugin_name=plugin_autocomplete)
    async def deactivate_plugin(
        self, interaction: discord.Interaction, plugin_name: str
    ) -> None:
        """Unloads a bot extension.

        Args:
            interaction (discord.Interaction): The interaction object.
            plugin_name (str): The name of the plugin to unload.
        """
        if not Permissions.has_permission("plugin_manager", interaction.user.id):
            await interaction.response.send_message(
                ErrMesagges.BAD_PERMISSIONS, ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            await self.bot.unload_extension(f"plugins.{plugin_name}.{plugin_name}")
            await self._sync_commands()
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` successfully deactivated!"
            )
        except discord.ExtensionNotFound:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` does not exist!", ephemeral=True
            )
        except discord.ExtensionNotLoaded:
            await interaction.followup.send(
                f"Plugin ``{plugin_name}`` is not currently active!", ephemeral=True
            )
        except Exception as e:
            logger.exception(f"Unexpected error unloading {plugin_name}")
            await interaction.followup.send(
                f"An unexpected error occurred: {e}", ephemeral=True
            )

    @app_commands.command(
        name="show_all_plugins", description="Lists all available plugins."
    )
    async def show_all_plugins(self, interaction: discord.Interaction) -> None:
        """Displays a list of all plugins available in the system.

        Args:
            interaction (discord.Interaction): The interaction object.
        """
        plugins_list = all_plugins()
        formatted_list = "\n".join(f"- {plugin}" for plugin in plugins_list)
        await interaction.response.send_message(
            f"**Available Plugins:**\n{formatted_list}"
        )