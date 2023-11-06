import logging
import os

import discord
from decouple import config
from discord.ext import commands
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# TODO use it
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_plugins():
    from abstract.cmds import all_plugins

    for plugin in all_plugins():
        bot.load_extension(f"plugins.{plugin}.{plugin}")


@bot.event
async def on_ready():
    load_plugins()

    print("Syncing commands.")
    await bot.sync_commands(
        guild_ids=[
            int(x) for x in config("DISCORD_SERVER_IDS").replace(" ", "").split(",")
        ]
    )
    print("Commands synced.")

    print("Bot je ready!")


bot.run(config("BOT_SECRET"))
