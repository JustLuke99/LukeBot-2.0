import asyncio
import logging
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands
from django.utils import timezone

from abstract.cmds import add_command, del_command, cmd_running
from abstract.constants import ErrMesagges
from abstract.permissions import Roles
from .utils import reddit_manager

logger = logging.getLogger(__name__)


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(reddit_manager.background_task())

    def cog_unload(self):
        self.bg_task.cancel()

    @app_commands.command(
        name="reddit_auto", description="Automatické posílání obrázků."
    )
    @app_commands.describe(duration="Doba trvání v minutách (1 až 60)")
    async def reddit_auto(self, interaction: discord.Interaction, duration: int):
        if not (1 <= duration <= 60):
            await interaction.response.send_message(
                "Doba trvání musí být mezi 1 a 60 minutami.", ephemeral=True
            )
            return

        if await cmd_running(interaction.channel_id, __name__):
            await interaction.response.send_message("Služba už běží.", ephemeral=True)
            return

        await interaction.response.send_message(f"Doba zapnutí je: {duration} minut")

        await add_command(interaction.channel_id, __name__)

        end_time = timezone.now() + timedelta(minutes=duration)

        try:
            while timezone.now() < end_time:
                if not await cmd_running(interaction.channel_id, __name__):
                    break

                image = await reddit_manager.get_valid_image()

                if image:
                    await interaction.channel.send(
                        f"Reddit: {image.subreddit}\n{image.url}"
                    )
                else:
                    logger.warning("No images available to send.")

                await asyncio.sleep(15)

        finally:
            await del_command(interaction.channel_id, __name__)

            try:
                msg = await interaction.channel.send("Posílání cecíků skončilo")
                await msg.add_reaction("🔃")
            except Exception:
                pass

    @app_commands.command(
        name="delete_all_photos", description="Smaže všechny obrázky z databáze."
    )
    async def delete_all_photos(self, interaction: discord.Interaction):
        if not Roles.has_role("admin", interaction.user.id):
            await interaction.response.send_message(
                ErrMesagges.BAD_PERMISSIONS, ephemeral=True
            )
            return

        await interaction.response.defer()

        await reddit_manager.delete_all_images()

        await interaction.followup.send("Databáze smazána")

    @app_commands.command(
        name="stop_auto_reddit", description="Zastaví posílání cecíků."
    )
    async def stop_auto_reddit(self, interaction: discord.Interaction):
        if not await cmd_running(interaction.channel_id, __name__):
            await interaction.response.send_message(
                "Žádné cecíky tu nevidím", ephemeral=True
            )
            return

        await del_command(interaction.channel_id, __name__)
        await interaction.response.send_message("Cecíky zastaveny")


async def setup(bot):
    await bot.add_cog(Reddit(bot))
