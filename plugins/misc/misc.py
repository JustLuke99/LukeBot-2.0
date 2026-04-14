import logging
import random

import discord
from discord.ext import commands
from django.utils import timezone

from bot.constants import ErrMessages
from bot.db_helpers import add_command, del_command
from bot.permissions import Roles, Permissions

logger = logging.getLogger(__name__)
__version__ = "2.0"


def setup(bot):
    bot.add_cog(Misc(bot))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_start = timezone.now()
        logger.info(f"Initializing misc module (version {__version__})")

    @commands.slash_command(name="ping", description="Vrátí odezvu bota.")
    async def ping(self, ctx):
        await ctx.respond(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.slash_command(name="50_50", description="Šance je 50/50 (0 nebo 1).")
    async def fredysgame(self, ctx):
        await ctx.respond(random.choice(["0", "1"]))

    @commands.slash_command(name="sexymetr", description="Vypočítá jak jsi sexy.")
    async def sexymetr(self, ctx, member: discord.Member = None):
        if member:
            await ctx.respond(f"{member} je sexy na {round(random.uniform(0, 102), 1)}%")
        else:
            await ctx.respond(f"Jsi sexy na {round(random.uniform(0, 102), 1)}%")

    @commands.slash_command(name="gay_calculator", description="Vypočítá jak moc si homo.")
    async def gay_calculator(self, ctx, member: discord.Member = None):
        if member:
            await ctx.respond(f"{member} je gay na {round(random.uniform(0, 100), 1)}%")
        else:
            await ctx.respond(f"Jsi gay na {round(random.uniform(0, 100), 1)}%")

    @commands.slash_command(name="dnessex", description="Řekne ti, zda budeš dnes mít sex.")
    async def dnessex(self, ctx):
        # Fixed: round(random.uniform(0, 35), 0) can be 0.0 (falsy) — wrong logic
        if random.uniform(0, 35) > 1.0:
            await ctx.respond("Dnes bohužel nebudeš mít sex <:sadcat:648293902587002929>")
        else:
            await ctx.respond(
                "Dnes budeš mít sex <:PogChamp:691295767993909291> Užij si to <:Kubaez:648295679499698176>"
            )

    @commands.slash_command(name="penis", description="Změří ti délku penisu.")
    async def penis(self, ctx):
        if Roles.is_girl(ctx.author):
            await ctx.respond("Holky penis nemají <:WeirdChamp:648310298087915550>")
        else:
            delka = round(random.uniform(2.5, 23.696), 2)
            await ctx.respond(f"Délka tvého penisu je {delka} cm.")

    @commands.slash_command(name="vagina", description="")
    async def vagina(self, ctx):
        if not Roles.is_girl(ctx.author):
            await ctx.respond("Kluci vaginu nemají <:WeirdChamp:648310298087915550>")
        else:
            delka = round(random.uniform(1, 3), 0)
            if delka == 1:
                emote = "hezky úzká <:Ahegeo:648301628025470986>"
            elif delka == 2:
                emote = "normální <:peepowow:648296420951982100>"
            else:
                emote = "rozježděná jak slovenský silnice <:kekw:655402255138422799>"
            await ctx.respond(f"Tvoje vagina je {emote}.")

    @commands.slash_command(name="hug", description="Hugni kamaráda.")
    async def hug(self, ctx, member: discord.Member):
        await ctx.respond(
            f"<:peepoHug:665605303437492224> {member.mention} <:loveheart:648286429104832532>"
        )

    @commands.slash_command(name="off", description="Vypnutí bota.")
    async def off(self, ctx):
        if not Permissions.has_permission("turn_off", ctx.author.id):
            await ctx.respond(
                ErrMessages.BAD_PERMISSIONS
                + f" Abych já nevypl tebe <:jebeToCoSiDalPrave:691704864488816660>"
            )
            return

        now = timezone.now()
        uptime = now - self.bot_start
        await ctx.respond(
            f"Odjíždím na dovolenou, mějte se tu hezky. Ahóóój <:loveheart:648286429104832532>```"
            f"Čas zapnutí: {str(self.bot_start).rsplit('.')[0]}\n"
            f"Čas vypnutí: {str(now).rsplit('.')[0]}\n"
            f"Celková doba zapnutí: {str(uptime).rsplit('.')[0]}```"
        )
        await self.bot.close()

    # TODO refactor this
    @commands.slash_command(name="count_messages", description="Spočítání zpráv.")
    async def message_counter(self, ctx, arg1=None, arg2=None):
        try:
            await add_command(ctx.channel.id, __name__)
        except commands.BadArgument as e:
            await ctx.respond(str(e))
            return

        start = timezone.now()
        await ctx.respond(
            "Začínám počítat zprávy, tohle bude chvilku trvat <:ocesSuck:653579725012467742>"
        )

        count_all = arg1 in ("all", "all+")
        progress_message = None
        num_of_ch = len(ctx.guild.text_channels)

        if count_all:
            m, _ = divmod(num_of_ch * 120, 60)
            h, m = divmod(m, 60)
            try:
                progress_message = await ctx.send(
                    f"```Očekávaná doba počítání je {h:d}h:{m:02d}m\nZatím je spočítáno 0%```"
                )
            except Exception:
                pass

        just_test = []
        messageCount_test = {}
        edit_prcnt = 0

        for channel in ctx.guild.text_channels:
            if (channel == ctx.channel) or count_all:
                tmp = 0
                messageCount_test[channel.name] = {}
                async for msg in channel.history(limit=99999):
                    if msg.author.name in messageCount_test[channel.name]:
                        messageCount_test[channel.name][msg.author.name] += 1
                    else:
                        messageCount_test[channel.name][msg.author.name] = 1
                    tmp += 1
                just_test.append({
                    "channel": channel.name,
                    "total_count": tmp,
                    "user_count": messageCount_test[channel.name],
                })

            edit_prcnt += 1
            if progress_message:
                m, _ = divmod((num_of_ch - edit_prcnt) * 120, 60)
                h, m = divmod(m, 60)
                try:
                    await progress_message.edit(
                        content=f"```Očekávaná doba počítání je {h:d}h:{m:02d}m\n"
                                f"Zatím je spočítáno {round(edit_prcnt / num_of_ch * 100, 2)}%```"
                    )
                except Exception:
                    pass

        total = {}
        celkem = 0
        send_help = ""

        for channel in just_test:
            celkem += channel["total_count"]
            send_help += (
                f"============= {channel['channel']} =============\n"
                f"Celkem odesláno zpráv roomce: {channel['total_count']}\n"
            )
            for name, count in channel["user_count"].items():
                if name in total:
                    total[name] += count
                else:
                    total[name] = count
                send_help += f"   {name}: {count}\n"
            send_help += "\n"

        now = timezone.now()
        send = f"Na serveru bylo posláno celkem {celkem} zpráv.\n"
        total = dict(sorted(total.items(), key=lambda item: item[1], reverse=True))
        for name, count in total.items():
            send += f"  {name}: {count}\n"

        timing = (
            f"\nstart: {str(start).rsplit('.')[0]}\n"
            f"konec: {str(now).rsplit('.')[0]}\n"
            f"Doba počítání: {str(now - start).rsplit('.')[0]}"
        )
        send_help_parts = send_help.split("\n\n")

        if arg1 == "all+":
            await ctx.send(f"```{send}{timing}```")
            for part in send_help_parts[:-1]:
                await ctx.send(f"```{part}```")
        elif count_all:
            await ctx.send(f"```{send}{timing}```")
        else:
            await ctx.send(f"```{send_help_parts[0]}{timing}```")

        await del_command(ctx.channel.id, __name__)

    @commands.command("roll")
    async def roll(self, ctx, *args):
        numeric = all(arg.isnumeric() for arg in args)
        if numeric:
            min_val = 0
            max_val = int(args[0])
            if len(args) == 2:
                min_val = int(args[0])
                max_val = int(args[1])
            await ctx.respond(
                f"Z intervalu {min_val} až {max_val} se vybralo číslo ``{random.randint(min_val, max_val)}``"
            )
        else:
            await ctx.respond(f"Z výběru {args} se vybrala možnost ``{random.choice(args)}``")
