from datetime import datetime
from datetime import timedelta

from discord.ext import commands

from .contants import ZKRATKY
from .utils import delay_check

__version__ = "2.0"


async def setup(bot):
    await bot.add_cog(TextResponse(bot))


class TextResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for i in ZKRATKY:
            ZKRATKY[i]["tmp"] = datetime.now() - timedelta(days=999)
        print(f"Initializing text_response module (version {__version__})")

    # TODO učesat
    @commands.Cog.listener()
    async def on_message(self, message):
        if ZKRATKY["badbot"]["reg"].search(message.content):
            await message.channel.send(
                "Drž piču zmrde <:reee:681088040797732868> Snažím se ze všech sil <:sadcat:648293902587002929>"
            )
        if message.author.bot:
            if ZKRATKY["stop"]["reg"].search(message.content):
                await message.channel.send(
                    "Sbohem kamaráde <:peeporain:648282034468290571> "
                )
            # elif zkratky["off"]["reg"].search(message.content) != None:
            #    await message.channel.send("Na tohle nemám.... du off... ")
            #    exit()
        if not message.author.bot:
            if ZKRATKY["gn"]["reg"].search(message.content):
                if delay_check("gn"):
                    return
                await message.channel.send("Gn! <:loveheart:648286429104832532>")
            elif ZKRATKY["gm"]["reg"].search(message.content):
                if delay_check("gm"):
                    return
                await message.channel.send(
                    "Dobré ránko <:loveheart:648286429104832532>"
                )
            elif ZKRATKY["purkyne"]["reg"].search(message.content):
                if delay_check("purkyne"):
                    return
                await message.add_reaction("💩")
            elif ZKRATKY["eo"]["reg"].search(message.content):
                if delay_check("eo"):
                    return
                await message.channel.send(
                    "<:pepega:648282034245992448> :mega: Eeeeeeeeeo"
                )
            elif ZKRATKY["ruby"]["reg"].search(message.content):
                if delay_check("ruby"):
                    return
                await message.channel.send("Hovnooo!")
            # elif ZKRATKY["party"]["reg"].search(message.content):
            #     if delay_check("party"):
            #         return
            #     await message.channel.send("Něco se blíží? <:PogChamp:691295767993909291> \nKontaktuji majitele... ")
            # elif ZKRATKY["tramvaj"]["reg"].search(message.content):
            #     if delay_check("tramvaj"):
            #         return
            #     await message.channel.send("Nemyslel si náhodou šalinu? <:WeirdChamp:648310298087915550>")
            elif ZKRATKY["sushi"]["reg"].search(message.content):
                if delay_check("sushi"):
                    return
                await message.add_reaction("🇲")
                await message.add_reaction("🇳")
                await message.add_reaction("🇦")
                await message.add_reaction("Ⓜ️")
                await message.add_reaction("<:Ahegeo:648301628025470986>")
            elif ZKRATKY["vodka"]["reg"].search(message.content):
                if delay_check("vodka"):
                    return
                await message.add_reaction("<:PogChamp:691295767993909291>")
                await message.channel.send(
                    "Čmuchám čmuchám dobrotu <:peepowow:648296420951982100> Nalijte rundu, já a můj majitel jsme již na cestě."
                )
            # elif ZKRATKY["kachna"]["reg"].search(message.content):
            #     await message.add_reaction("🦆")
            #     if delay_check("kachna"):
            #         return
            #     await message.channel.send(
            #         "Vycházím. Kupte mi jedno malý pivo a 2 tousty! <:peepolove:669225702511476758>")
            elif ZKRATKY["flex"]["reg"].search(message.content):
                if delay_check("flex"):
                    return
                # await message.channel.send("Mr. flex osobně? <:PogChamp:691295767993909291> Můžu poprosit podpis? <:peepowow:648296420951982100>")
                await message.channel.send(
                    "Divný flex, ale ok <:kekw:655402255138422799>"
                )
            # elif ZKRATKY["černoch"]["reg"].search(message.content):
            #     if delay_check("černoch"):
            #         return
            #     await message.add_reaction("🇧")
            #     await message.add_reaction("🇷")
            #     await message.add_reaction("🇺")
            #     await message.add_reaction("🇭")
            #     await message.add_reaction("<:wtf:684418064808149003>")
            # elif ZKRATKY["ahoj"]["reg"].search(message.content):
            #     if delay_check("ahoj"): return
            #     await message.channel.send("Nazdar chlapáku <:Baosexy:652605568783089694>")
            elif ZKRATKY["hihahuhahi"]["reg"].search(message.content):
                if delay_check("hihahuhahi"):
                    return
                await message.channel.send("Debile! <:LukeRage:652604361561604096>")
            elif ZKRATKY["stopemote"]["reg"].search(message.content):
                if delay_check("stopemote"):
                    return
                await message.channel.send(
                    "https://media.giphy.com/media/NMHpkm0MPar2U/giphy.gif"
                )
            elif ZKRATKY["okBot"]["reg"].search(message.content):
                if delay_check("okBot"):
                    return
                await message.channel.send(
                    "Omlouvám se za malé nedopatření... Chyba bude nahlášena a opravena <:peepowow:648296420951982100>"
                )
            elif ZKRATKY["fuchs"]["reg"].search(message.content):
                if delay_check("fuchs"):
                    return
                await message.add_reaction("<:aPES_Spit:>")
