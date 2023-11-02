import asyncio
import datetime
import importlib
import os
import pytz
from datetime import datetime, timedelta

from abstract.cmds import *
from .constants import PARSER_DIRECTORY, DISCORD_ROOMS

__version__ = "1.0"


def setup(bot):
    bot.add_cog(Lunch(bot))


class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"Initializing lunch module (version {__version__})")
        self.bg_task = self.bot.loop.create_task(self.auto_send_lunches())

    async def i_sleep_here(self):
        now = datetime.now(pytz.timezone('Europe/Prague'))

        target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += timedelta(days=1)

        delta = target_time - now

        await asyncio.sleep(delta.total_seconds())

    async def send_lunches(self, lunches):
        for room in DISCORD_ROOMS:
            channel = self.bot.get_channel(room)
            # await channel.purge(limit=100)
            for lunch in lunches:
                await channel.send('\n'.join(lunch))

    @staticmethod
    async def get_files():
        path = os.path.join(os.path.dirname(__file__), PARSER_DIRECTORY)
        files = os.listdir(path)

        return files

    async def auto_send_lunches(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.i_sleep_here()

            files = await self.get_files()

            send_data = []
            for file in files:
                if not file.endswith(".py"):
                    continue

                module_name = file[:-3]
                module = importlib.import_module(f'plugins.lunch.{PARSER_DIRECTORY}.{module_name}')

                parser_function = getattr(module, f'{module_name}_parser', None)
                if parser_function:
                    lunch = parser_function()
                    lunch.insert(0, f"# {module_name} #")
                    send_data.append(lunch)
            await self.send_lunches(send_data)

    def cog_unload(self):
        if self.bg_task:
            self.bg_task.cancel()
