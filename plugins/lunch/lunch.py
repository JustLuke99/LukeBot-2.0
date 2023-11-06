import asyncio
import datetime
import importlib
import os
import time
from datetime import datetime, timedelta

import pytz
from decouple import config

from abstract.cmds import *
from .constants import PARSER_DIRECTORY

__version__ = "1.0"


def setup(bot):
    bot.add_cog(Lunch(bot))


class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lunch_rooms = [
            x for x in config("LUNCH_ROOMS").replace(" ", "").split(",")
        ]

        self.bg_task = self.bot.loop.create_task(self.auto_send_lunches())

        print(f"Initializing lunch module (version {__version__})")

    async def i_sleep_here(self):
        now = datetime.now(pytz.timezone("Europe/Prague"))

        target_time = now.replace(hour=10, minute=10, second=0, microsecond=0)

        if now > target_time:
            target_time += timedelta(days=1)

        delta = target_time - now

        await asyncio.sleep(delta.total_seconds())

    async def send_lunches(self, lunches):
        for room in self.lunch_rooms:
            channel = self.bot.get_channel(int(room))
            await channel.purge(limit=100)
            for lunch in lunches:
                await channel.send("\n".join(lunch))
                time.sleep(0.2)

    @staticmethod
    async def get_files():
        path = os.path.join(os.path.dirname(__file__), PARSER_DIRECTORY)
        files = os.listdir(path)

        return files

    async def auto_send_lunches(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            # await self.i_sleep_here()

            files = await self.get_files()

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
                    except:
                        lunch = ["Obědy se nepodařilo rozparsovat"]
                    lunch.insert(0, f"# {module_name} #")
                    send_data.append(lunch)

            await self.send_lunches(send_data)

    def cog_unload(self):
        if self.bg_task:
            self.bg_task.cancel()
