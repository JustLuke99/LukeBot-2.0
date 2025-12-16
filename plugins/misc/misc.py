import logging
import random
from typing import Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import utcnow

# Assuming these modules exist in your project structure
from abstract.cmds import add_command, del_command
from abstract.constants import ErrMesagges
from abstract.permissions import Roles, Permissions

logger = logging.getLogger(__name__)

__version__ = "2.6.4"


class Misc(commands.Cog):
    """A collection of miscellaneous utility and fun commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the Misc cog.

        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        self.bot_start_time = utcnow()
        logger.info(f"Initializing Misc module (version {__version__})")

    @app_commands.command(name="ping", description="Returns the bot's latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Responds with the current latency in milliseconds."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency}ms")

    @app_commands.command(name="50_50", description="Returns 0 or 1.")
    async def fifty_fifty(self, interaction: discord.Interaction) -> None:
        """Randomly chooses between 0 and 1."""
        await interaction.response.send_message(random.choice(["0", "1"]))

    @app_commands.command(name="sexymetr", description="Calculates sexiness.")
    async def sexymeter(
            self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """Generates a random percentage of sexiness for a user.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (Optional[discord.Member]): The target member. Defaults to user.
        """
        target = member or interaction.user
        percentage = round(random.uniform(0, 102), 1)
        target_name = (
            "You are" if target == interaction.user else f"{target.display_name} is"
        )
        await interaction.response.send_message(f"{target_name} sexy na {percentage}%")

    @app_commands.command(
        name="gay_calculator", description="Calculates gay percentage."
    )
    async def gay_calculator(
            self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """Generates a random percentage representing how gay a user is.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (Optional[discord.Member]): The target member. Defaults to user.
        """
        target = member or interaction.user
        percentage = round(random.uniform(0, 100), 1)
        target_name = (
            "jsi" if target == interaction.user else f"{target.display_name} je"
        )
        await interaction.response.send_message(f"{target_name} gay na {percentage}%")

    @app_commands.command(
        name="dnessex", description="Predicts if you will have sex today."
    )
    async def today_sex(self, interaction: discord.Interaction) -> None:
        """Randomly determines if the user will get lucky today."""
        chance = round(random.uniform(0, 35), 0)
        if chance:
            await interaction.response.send_message(
                "Dnes bohužel nebudeš mít sex <:sadcat:648293902587002929>"
            )
        else:
            await interaction.response.send_message(
                "Dnes budeš mít sex <:PogChamp:691295767993909291> "
                "Užij si to <:Kubaez:648295679499698176>"
            )

    @app_commands.command(name="penis", description="Measures penis length.")
    async def penis_length(self, interaction: discord.Interaction) -> None:
        """Generates a random length. Returns specific message for female role."""
        if Roles.is_girl(interaction.user.id):
            await interaction.response.send_message(
                "Holky penis nemají <:WeirdChamp:648310298087915550>"
            )
            return

        length = round(random.uniform(2.5, 23.696), 2)
        await interaction.response.send_message(f"Délka tvého penisu je {length} cm.")

    @app_commands.command(name="vagina", description="Describes vagina status.")
    async def vagina_status(self, interaction: discord.Interaction) -> None:
        """Generates a random description. Returns specific message for non-girls."""
        if not Roles.is_girl(interaction.user.id):
            await interaction.response.send_message(
                "Kluci vaginu nemají <:WeirdChamp:648310298087915550>"
            )
            return

        variant = round(random.uniform(1, 3), 0)
        emotes = {
            1: "hezky úzká <:Ahegeo:648301628025470986>",
            2: "normální <:peepowow:648296420951982100>",
            3: "rozježděná jak slovenský silnice <:kekw:655402255138422799>",
        }
        await interaction.response.send_message(
            f"Tvoje vagina je {emotes.get(variant, 'normální')}."
        )

    @app_commands.command(name="hug", description="Hug a friend.")
    async def hug(self, interaction: discord.Interaction, member: discord.Member) -> None:
        """Sends a hug message to the target member.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to hug.
        """
        await interaction.response.send_message(
            f"<:peepoHug:665605303437492224> {member.mention} "
            f"<:loveheart:648286429104832532>"
        )

    @app_commands.command(
        name="msg", description="Sends a message to a specific channel."
    )
    @app_commands.describe(
        channel="The channel to send the message to",
        message="The content of the message",
    )
    async def send_message(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            message: str,
    ) -> None:
        """Sends a message to a mentioned channel. Requires permissions.

        Args:
            interaction (discord.Interaction): The interaction object.
            channel (discord.TextChannel): The target channel.
            message (str): The message content.
        """
        if not Permissions.has_permission("send_messages", interaction.user.id):
            await interaction.response.send_message(
                ErrMesagges.BAD_PERMISSIONS, ephemeral=True
            )
            return

        await channel.send(message)
        # Interaction must always be responded to
        await interaction.response.send_message(
            f"Message sent to {channel.mention}.", ephemeral=True
        )

    @app_commands.command(name="off", description="Turns off the bot.")
    async def shutdown(self, interaction: discord.Interaction) -> None:
        """Shuts down the bot gracefully. Requires permissions."""
        if not Permissions.has_permission("turn_off", interaction.user.id):
            await interaction.response.send_message(
                f"{ErrMesagges.BAD_PERMISSIONS} "
                "Abych já nevypl tebe <:jebeToCoSiDalPrave:691704864488816660>",
                ephemeral=True,
            )
            return

        now = utcnow()
        uptime = now - self.bot_start_time

        info_block = (
            f"Čas zapnutí: {self.bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Čas vypnutí: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Celková doba zapnutí: {str(uptime).split('.')[0]}"
        )

        await interaction.response.send_message(
            f"Odjíždím na dovolenou, mějte se tu hezky. Ahóóój "
            f"<:loveheart:648286429104832532>```\n{info_block}```"
        )
        await self.bot.close()

    @app_commands.command(
        name="count_messages", description="Counts messages in channels."
    )
    @app_commands.describe(
        scope="Where to count (current channel or whole server)",
        detailed="Show detailed per-user stats",
    )
    async def message_counter(
            self,
            interaction: discord.Interaction,
            scope: Literal["Current Channel", "All Channels"] = "Current Channel",
            detailed: bool = False,
    ) -> None:
        """Counts messages in the guild or channel.

        This is a resource-intensive operation.

        Args:
            interaction (discord.Interaction): The interaction object.
            scope (str): Scope of counting.
            detailed (bool): Whether to show per-user statistics.
        """
        # 1. Register command running state
        try:
            await add_command(interaction.channel_id, __name__)
        except Exception as e:
            await interaction.response.send_message(
                f"Cannot start counter: {e}", ephemeral=True
            )
            return

        # 2. Defer response (counting takes time)
        # We must defer because this operation will likely take > 3 seconds
        await interaction.response.defer()

        start_time = utcnow()

        # NOTE: After defer(), we use interaction.followup.send()
        status_msg = await interaction.followup.send(
            "Začínám počítat zprávy, tohle bude chvilku trvat "
            "<:ocesSuck:653579725012467742>"
        )

        # 3. Determine channels to scan
        if scope == "All Channels":
            channels = interaction.guild.text_channels
        else:
            channels = [interaction.channel]

        total_server_messages = 0
        channel_stats = []

        # 4. Processing Loop
        total_channels = len(channels)

        try:
            for index, channel in enumerate(channels, 1):
                channel_msg_count = 0
                user_counts = {}

                # Updating status every 5 channels or for single channel
                if scope == "All Channels" and index % 5 == 0:
                    percent = round((index / total_channels) * 100)
                    try:
                        await status_msg.edit(
                            content=f"Počítám... {percent}% hotovo ({index}/{total_channels} roomek)."
                        )
                    except discord.HTTPException:
                        pass

                # History iteration
                # Note: 'limit=None' can be very slow.
                async for msg in channel.history(limit=None):
                    if msg.author.bot:
                        continue

                    user_counts[msg.author.name] = (
                            user_counts.get(msg.author.name, 0) + 1
                    )
                    channel_msg_count += 1

                channel_stats.append(
                    {
                        "name": channel.name,
                        "total": channel_msg_count,
                        "users": user_counts,
                    }
                )
                total_server_messages += channel_msg_count

        except Exception as e:
            logger.error(f"Error during message counting: {e}")
            await interaction.followup.send("Nastala chyba při počítání.")
            await del_command(interaction.channel_id, __name__)
            return

        # 5. Aggregating Results
        global_user_stats = {}
        report_details = ""

        for stat in channel_stats:
            report_details += (
                f"============= {stat['name']} =============\n"
                f"Celkem odesláno zpráv: {stat['total']}\n"
            )
            for user, count in stat['users'].items():
                global_user_stats[user] = global_user_stats.get(user, 0) + count
                if detailed:
                    report_details += f"   {user}: {count}\n"
            report_details += "\n"

        # Sorting global stats
        sorted_users = sorted(
            global_user_stats.items(), key=lambda item: item[1], reverse=True
        )

        summary = f"Na serveru bylo posláno celkem {total_server_messages} zpráv.\n"
        for user, count in sorted_users:
            summary += f"  {user}: {count}\n"

        duration = str(utcnow() - start_time).split(".")[0]
        footer = (
            f"\nstart: {start_time.strftime('%H:%M:%S')}\n"
            f"konec: {utcnow().strftime('%H:%M:%S')}\n"
            f"Doba počítání: {duration}"
        )

        # 6. Sending Output via Followup (since we deferred)
        if detailed and scope == "All Channels":
            # Send summary first
            await interaction.followup.send(f"```{summary}\n{footer}```")

            # Send details in chunks (Discord limit is 2000 chars)
            chunks = [
                report_details[i: i + 1900]
                for i in range(0, len(report_details), 1900)
            ]
            for chunk in chunks:
                await interaction.followup.send(f"```{chunk}```")
        else:
            final_msg = (
                f"{report_details if scope == 'Current Channel' else summary}\n{footer}"
            )
            if len(final_msg) > 1900:
                await interaction.followup.send(f"```{summary}\n{footer}```")
            else:
                await interaction.followup.send(f"```{final_msg}```")

        # 7. Cleanup
        await del_command(interaction.channel_id, __name__)

    @app_commands.command(name="roll", description="Rolls a random number.")
    @app_commands.describe(
        min_val="Minimum value (default 0)", max_val="Maximum value"
    )
    async def roll(
            self, interaction: discord.Interaction, max_val: int, min_val: int = 0
    ) -> None:
        """Rolls a random number between min and max.

        Args:
            interaction (discord.Interaction): The interaction object.
            max_val (int): The upper bound.
            min_val (int): The lower bound. Default is 0.
        """
        if min_val > max_val:
            min_val, max_val = max_val, min_val

        result = random.randint(min_val, max_val)
        await interaction.response.send_message(
            f"Z intervalu {min_val} až {max_val} se vybralo číslo ``{result}``"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Misc(bot))