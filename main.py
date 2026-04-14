import logging
import os

import django
import discord
from decouple import config
from discord.ext import commands

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class LukeBot(commands.Bot):
    """Main bot class. Plugins are loaded in setup_hook() — guaranteed to run exactly once."""

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(command_prefix="/", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        """Called by the framework exactly once on startup — the correct place to load extensions."""
        from bot.plugin_loader import all_plugins

        logger.info("Loading plugins...")
        for plugin in all_plugins():
            try:
                await self.load_extension(f"plugins.{plugin}.{plugin}")
                logger.info(f"Plugin loaded: {plugin}")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin}: {e}")

        logger.info("Syncing commands...")
        guild_ids_raw = config("DISCORD_SERVER_IDS", default="")
        if guild_ids_raw:
            for guild_id in [int(x) for x in guild_ids_raw.replace(" ", "").split(",") if x]:
                await self.sync_commands(guild_ids=[guild_id])
                logger.info(f"Commands synced for guild {guild_id}")
        else:
            await self.sync_commands()
            logger.info("Global command sync complete.")

    async def on_ready(self) -> None:
        logger.info(f"Bot ready: {self.user} (ID: {self.user.id})")


if __name__ == "__main__":
    bot = LukeBot()
    bot.run(config("BOT_SECRET"))
