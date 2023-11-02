import datetime
import random

import discord
from discord.ext import commands
from abstract.cmds import *

from abstract.constants import ErrMesagges
from abstract.permissions import Roles, Permissions
from data.models import *

__version__ = "2.0"


def setup(bot):
    bot.add_cog(Misc(bot))


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot_start = datetime.utcnow()

        self.messageCount = {}
        self.messageCount_test = {}
        print(f"Initializing misc module (version {__version__})")

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
            await ctx.respond(f"jsi gay na {round(random.uniform(0, 100), 1)}%")

    @commands.slash_command(name="dnessex", description="Řekne ti, zda budeš dnes mít sex.")
    async def dnessex(self, ctx):
        if round(random.uniform(0, 35), 0):
            await ctx.respond(f"Dnes bohužel nebudeš mít sex <:sadcat:648293902587002929>")
        else:
            await ctx.respond(
                f"Dnes budeš mít sex <:PogChamp:691295767993909291> Užij si to <:Kubaez:648295679499698176>")

    @commands.slash_command(name="penis", description="Změří ti délku penisu.")
    async def penis(self, ctx):
        if Roles.is_girl(ctx.author.id):
            await ctx.respond("Holky penis nemají <:WeirdChamp:648310298087915550>")
        else:
            delka = round(random.uniform(2.5, 23.696), 2)
            await ctx.respond(f"Délka tvého penisu je {delka} cm.")

    # TODO dopsat desc
    @commands.slash_command(name="vagina", description="")
    async def vagina(self, ctx):
        if not Roles.is_girl(ctx.author.id):
            await ctx.respond("Kluci vaginu nemají <:WeirdChamp:648310298087915550>")
        else:
            delka = round(random.uniform(1, 3), 0)
            if delka == 1:
                emote = "hezky úzká <:Ahegeo:648301628025470986>"
            elif delka == 2:
                emote = "normální <:peepowow:648296420951982100>"
            elif delka == 3:
                emote = "rozježděná jak slovenský silnice <:kekw:655402255138422799>"
            await ctx.respond(f"Tvoje vagina je {emote}.")

    @commands.slash_command(name="hug", description="Hugni kamaráda.")
    async def hug(self, ctx, member: discord.Member):
        await ctx.respond(f"<:peepoHug:665605303437492224> {member.mention} <:loveheart:648286429104832532>")

    # @commands.slash_command(name="hug", description="Hugni kamaráda.")
    # async def hug2(self, ctx, member: discord.Member):
    #     await ctx.respond(f"<:peepoHug:665605303437492224> {member} <:loveheart:648286429104832532>")

    @commands.slash_command(name="msg", description="Tajná muška funkce :)")
    async def msg(self, ctx, *args):
        if Permissions.has_permission("send_messages", ctx.author.id):
            await ctx.message.channel_mentions[0].respond(" ".join(args[1:]))
        else:
            await ctx.respond(ErrMesagges.BAD_PERMISSIONS)

    @commands.slash_command(name="off", description="Vypnutí bota.")
    async def off(self, ctx):
        if not Permissions.has_permission("turn_off", ctx.author.id):
            await ctx.respond(
                ErrMesagges.BAD_PERMISSIONS + f" Abych já nevypl tebe <:jebeToCoSiDalPrave:691704864488816660>")
            return

        await ctx.respond(
            f"Odjíždím na dovolenou, mějte se tu hezky.  Ahóóój <:loveheart:648286429104832532>```"
            f"Čas zapnutí: {str((self.bot_start)).rsplit('.')[0]} \n"
            f"Čas vypnutí: {str((datetime.utcnow())).rsplit('.')[0]} \n"
            f"Celková doba zapnutí: {str((datetime.utcnow() - self.bot_start)).rsplit('.')[0]}```")
        exit()

    # TODO refactor this
    @commands.slash_command(name="count_messages", description="Spočítání zpráv.")
    async def message_counter(self, ctx, arg1=None, arg2=None):
        try:
            await add_command(ctx.channel.id, __name__)
        except commands.BadArgument as e:
            await ctx.respond(f"{e}")
            return
        start = datetime.utcnow()
        await ctx.respond("Začínám počítat zprávy, tohle bude chvilku trvat <:ocesSuck:653579725012467742>")
        just_test = []
        send = ""
        send_help = ""
        num_of_ch = len(ctx.guild.text_channels)
        limit = 99999
        if arg1 == "all" or arg1 == "all+":
            m, _ = divmod(num_of_ch * 120, 60)
            h, m = divmod(m, 60)
            try:
                message = await ctx.send(f"```Očekávaná doba počítání je {h:d}h:{m:02d}m\nZatím je spočítáno 0%```")
            except:
                ...
            count_all = True
            # if arg2:
            #    limit = arg2
        elif not arg1:
            count_all = False
        else:
            ...
        # for guild in self.bot.guilds:
        # if guild == ctx.guild:#print(guild)
        edit_prcnt = 0
        messageCount_test = {}
        for channel in ctx.guild.text_channels:
            if (channel == ctx.channel) or count_all:
                tmp = 0
                messageCount_test[channel.name] = dict()
                async for msg in channel.history(limit=99999):
                    if msg.author.name in messageCount_test[channel.name]:
                        messageCount_test[channel.name][msg.author.name] += 1
                    else:
                        messageCount_test[channel.name][msg.author.name] = 1
                    tmp += 1
                just_test.append(
                    {"channel": channel.name, "total_count": tmp, "user_count": messageCount_test[channel.name]})
            edit_prcnt += 1
            m, _ = divmod((num_of_ch - edit_prcnt) * 120, 60)
            h, m = divmod(m, 60)
            try:
                await message.edit(
                    content=f"```Očekávaná doba počítání je {h:d}h:{m:02d}m\nZatím je spočítáno {round(edit_prcnt / num_of_ch * 100, 2)}%```")
            except:
                ...
        total = dict()
        celkem = 0
        names = None
        names2 = None
        for channel in just_test:
            celkem += channel["total_count"]
            send_help += f"============= {channel['channel']} =============\nCelkem odesláno zpráv roomce: {str(channel['total_count'])}\n"
            names = channel["user_count"].keys()
            for name in names:
                if name in total:
                    total[name] += channel["user_count"][name]
                else:
                    total[name] = channel["user_count"][name]
                send_help += f"   {name}: {str(channel['user_count'][name])}\n"
            send_help += "\n"
        send = f"Na serveru bylo posláno celkem {celkem} zpráv.\n"
        send_help = send_help.split("\n\n")
        total = dict(sorted(total.items(), key=lambda item: item[1], reverse=True))
        names2 = total.keys()
        for name in names2:
            send += f"  {name}: {total[name]}\n"

        if arg1 == "all+":
            await ctx.send(
                f"```{send}\nstart: {str((start)).rsplit('.')[0]} \nkonec: {str((datetime.utcnow())).rsplit('.')[0]}\nDoba počítání: {str((datetime.utcnow() - start)).rsplit('.')[0]}```")
            for i in range(len(send_help) - 1):
                await ctx.send(f"```{send_help[i]}```")
        elif count_all:
            await ctx.send(
                f"```{send}\nstart: {str((start)).rsplit('.')[0]} \nkonec: {str((datetime.utcnow())).rsplit('.')[0]}\nDoba počítání: {str((datetime.utcnow() - start)).rsplit('.')[0]}```")
        else:
            await ctx.send(
                f"```{send_help[0]}\n\nstart: {str((start)).rsplit('.')[0]} \nkonec: {str((datetime.utcnow())).rsplit('.')[0]}\nDoba počítání: {str((datetime.utcnow() - start)).rsplit('.')[0]}```")
        await del_command(ctx.channel.id, __name__)
        return

    # TODO dodělat
    @commands.command("roll")
    async def roll(self, ctx, *args):
        numeric = True

        for arg in args:
            if not arg.isnumeric():
                numeric = False

        if numeric:
            min = 0
            max = int(args[0])
            if len(args) == 2:
                min = int(args[0])
                max = int(args[1])

            await ctx.respond(f"Z intervalu {min} až {max} se vybralo číslo ``{random.randint(min, max)}``")
        else:
            await ctx.respond(f"Z výběru {args} se vybrala možnost ``{random.choice(args)}``")
