from discord.ext.commands import Converter

from abstract.cmds import *
from abstract.constants import ErrMesagges
from abstract.permissions import Roles
from .utils import *

__version__ = "2.0"


def setup(bot):
    bot.add_cog(Reddit(bot))


class DurationConverter(Converter):
    # TODO dodělat, že se error propíše
    async def convert(self, ctx, argument):
        try:
            value = int(argument)
            if 1 <= value <= 60:
                return value
            else:
                raise commands.BadArgument("Duration must be between 1 and 60 minutes.")
        except ValueError:
            raise commands.BadArgument("Duration must be a valid integer.")


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id=config("REDDIT_CLIENT"), client_secret=config("REDDIT_SECRET"),
                                  user_agent='DiscordBot', check_for_async=False)

        asyncio.ensure_future(del_all_commands())
        asyncio.ensure_future(check_reddit_images())
        print(f"Initializing reddit module (version {__version__})")

    @commands.slash_command(name="reddit_auto", description="Automatické posílání cecíků.")
    async def reddit_auto(self, ctx, duration: DurationConverter):
        try:
            await add_command(ctx.channel.id, __name__)
            await ctx.respond(f"Doba zapnutí je: {duration} minut")
        except commands.BadArgument as e:
            await ctx.respond(f"{e}")
            return

        end_time = datetime.now() + timedelta(minutes=duration)

        while datetime.now() < end_time:
            image = await get_image()
            await ctx.send(f"Reddit: {image.subreddit}\n{image.url}")

            await asyncio.sleep(15)

        await del_command(ctx.channel.id, __name__)
        msg = await ctx.send("Posílání cecíků skončilo")
        # TODO dodělat
        await msg.add_reaction("🔃")

    @commands.slash_command(name="delete_all_photos", description="Smaže všechny obrázky z databáze.")
    async def delete_all_photos(self, ctx):
        if not Roles.has_role("admin", ctx.author.id):
            await ctx.send(ErrMesagges.BAD_PERMISSIONS)

        await del_all_images()
        await ctx.respond("Databáze smazána")

    # TODO dodělat, nefunkční
    @commands.slash_command(name="stop_auto_reddit", description="Zastaví posílání cecíků")
    async def stop_auto_reddit(self, ctx):
        if not await cmd_running(ctx.channel.id, __name__):
            await ctx.respond("Žádné cecíky tu nevidím")
            return

        # self.stop_reddit.append(ctx.channel.id)
        await del_command(ctx.channel.id, __name__)
        await ctx.respond("Cecíky zastaveny")

