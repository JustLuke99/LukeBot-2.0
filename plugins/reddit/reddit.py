import asyncio
import logging
from datetime import timedelta

from discord.ext import commands
from discord.ext.commands import Converter, BadArgument
from django.utils import timezone

from abstract.cmds import add_command, del_command, cmd_running
from abstract.constants import ErrMesagges
from abstract.permissions import Roles
from .utils import reddit_manager

logger = logging.getLogger(__name__)


class DurationConverter(Converter):
    async def convert(self, ctx, argument):
        try:
            value = int(argument)
            if 1 <= value <= 60:
                return value
            raise BadArgument("Duration must be between 1 and 60 minutes.")
        except ValueError:
            raise BadArgument("Duration must be a valid integer.")


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(reddit_manager.background_task())

    def cog_unload(self):
        self.bg_task.cancel()

    @commands.slash_command(
        name="reddit_auto", description="Automatické posílání cecíků."
    )
    async def reddit_auto(self, ctx, duration: DurationConverter):
        if await cmd_running(ctx.channel.id, __name__):
            await ctx.respond("Služba už běží.")
            return

        await add_command(ctx.channel.id, __name__)
        await ctx.respond(f"Doba zapnutí je: {duration} minut")

        end_time = timezone.now() + timedelta(minutes=duration)

        try:
            while timezone.now() < end_time:
                if not await cmd_running(ctx.channel.id, __name__):
                    break

                image = await reddit_manager.get_valid_image()

                if image:
                    await ctx.send(f"Reddit: {image.subreddit}\n{image.url}")
                else:
                    logger.warning("No images available to send.")

                await asyncio.sleep(15)

        finally:
            await del_command(ctx.channel.id, __name__)

            try:
                msg = await ctx.send("Posílání cecíků skončilo")
                await msg.add_reaction("🔃")
            except Exception:
                pass

    @commands.slash_command(
        name="delete_all_photos", description="Smaže všechny obrázky z databáze."
    )
    async def delete_all_photos(self, ctx):
        if not Roles.has_role("admin", ctx.author.id):
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)
            return

        await reddit_manager.delete_all_images()
        await ctx.respond("Databáze smazána")

    @commands.slash_command(
        name="stop_auto_reddit", description="Zastaví posílání cecíků"
    )
    async def stop_auto_reddit(self, ctx):
        if not await cmd_running(ctx.channel.id, __name__):
            await ctx.respond("Žádné cecíky tu nevidím")
            return

        await del_command(ctx.channel.id, __name__)
        await ctx.respond("Cecíky zastaveny")


def setup(bot):
    bot.add_cog(Reddit(bot))