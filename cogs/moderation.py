from datetime import timedelta


import discord

from discord.ext import commands

from discord import app_commands


from utils.permissions import is_admin



class Moderation(commands.Cog):


    def __init__(self, bot):

        self.bot = bot




    @app_commands.command(

        name="mute",

        description="Выдать мут"

    )

    async def mute(

        self,

        interaction: discord.Interaction,

        player: discord.Member,

        minutes: int,

        reason: str

    ):


        if not is_admin(interaction.user):

            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )



        await player.timeout(

            discord.utils.utcnow()

            + timedelta(minutes=minutes),

            reason=reason

        )



        await interaction.response.send_message(

            f"🔇 {player.mention} получил мут"

        )





    @app_commands.command(

        name="unmute",

        description="Снять мут"

    )

    async def unmute(

        self,

        interaction,

        player: discord.Member

    ):


        if not is_admin(interaction.user):

            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )



        await player.timeout(

            None

        )



        await interaction.response.send_message(

            f"✅ Мут снят с {player.mention}"

        )





async def setup(bot):

    await bot.add_cog(

        Moderation(bot)

    )