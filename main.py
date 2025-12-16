import logging
import os

import discord
from decouple import config
from discord.ext import commands
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MujBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        print("--- Načítám pluginy ---")

        from abstract.cmds import all_plugins

        for plugin in all_plugins():
            try:
                await self.load_extension(f"plugins.{plugin}.{plugin}")
                print(f"Načten plugin: {plugin}")
            except Exception as e:
                logger.error(f"Chyba při načítání pluginu {plugin}: {e}")

        print("--- Synchronizace Commandů ---")

        guild_ids_raw = config("DISCORD_SERVER_IDS", default="")
        if guild_ids_raw:
            guild_ids_list = [
                int(x) for x in guild_ids_raw.replace(" ", "").split(",") if x
            ]

            for guild_id in guild_ids_list:
                guild_object = discord.Object(id=guild_id)

                self.tree.copy_global_to(guild=guild_object)

                await self.tree.sync(guild=guild_object)
                print(f"Synchronizováno pro Guild ID: {guild_id}")
        else:
            print("Žádné ID serverů v configu. Synchronizuji globálně...")
            await self.tree.sync()

    async def on_ready(self):
        print(f"Bot je ready! Přihlášen jako {self.user} (ID: {self.user.id})")
        print("------")


if __name__ == "__main__":
    bot = MujBot()
    bot.run(config("BOT_SECRET"))
