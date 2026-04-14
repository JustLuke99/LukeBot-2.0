import asyncio
import importlib
import logging
import os
from datetime import datetime, timedelta

import pytz
from decouple import config
from discord.ext import commands

from .constants import PARSER_DIRECTORY

logger = logging.getLogger(__name__)
__version__ = "1.0"


def setup(bot):
    bot.add_cog(Lunch(bot))


class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lunch_rooms = [x for x in config("LUNCH_ROOMS").replace(" ", "").split(",")]
        if self.lunch_rooms:
            self.bg_task = self.bot.loop.create_task(self.auto_send_lunches())
        logger.info(f"Initializing lunch module (version {__version__})")

    async def _sleep_until_lunch_time(self) -> None:
        now = datetime.now(pytz.timezone("Europe/Prague"))
        target_time = now.replace(hour=10, minute=10, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        delta = target_time - now
        await asyncio.sleep(delta.total_seconds())

    async def send_lunches(self, lunches: list) -> None:
        for room_id in self.lunch_rooms:
            channel = self.bot.get_channel(int(room_id))
            if channel is None:
                logger.warning(f"Channel {room_id} not found.")
                continue
            await channel.purge(limit=100)
            for lunch in lunches:
                await channel.send("\n".join(lunch))
                await asyncio.sleep(0.2)

    @staticmethod
    def _get_parser_files() -> list:
        path = os.path.join(os.path.dirname(__file__), PARSER_DIRECTORY)
        return os.listdir(path)

    async def auto_send_lunches(self) -> None:
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            await self._sleep_until_lunch_time()

            files = self._get_parser_files()
            send_data = []

            for file in files:
                if not file.endswith(".py") or "__" in file:
                    continue

                module_name = file[:-3]
                module = importlib.import_module(
                    f"plugins.lunch.{PARSER_DIRECTORY}.{module_name}"
                )
                parser_function = getattr(module, f"{module_name}_parser", None)

                if parser_function:
                    try:
                        lunch = parser_function()
                    except Exception as e:
                        logger.error(f"Parser {module_name} failed: {e}")
                        lunch = [f"Obědy z {module_name} se nepodařilo načíst"]
                    lunch.insert(0, f"# {module_name} #")
                    send_data.append(lunch)

            await self.send_lunches(send_data)

    def cog_unload(self):
        if self.bg_task:
            self.bg_task.cancel()
