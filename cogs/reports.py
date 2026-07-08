import discord

from discord.ext import commands
from discord import app_commands

from views.close_buttons import CloseView


class ReportForm(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Жалоба"
        )


        self.player = discord.ui.TextInput(
            label="Ник нарушителя"
        )


        self.reason = discord.ui.TextInput(
            label="Причина",
            style=discord.TextStyle.long
        )


        self.add_item(self.player)
        self.add_item(self.reason)



    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild
        member = interaction.user


        channel = await guild.create_text_channel(

            name=f"жалоба-{member.name}"

        )


        embed = discord.Embed(

            title="⚠️ Новая жалоба"

        )


        embed.add_field(

            name="Отправил",

            value=member.mention,

            inline=False

        )


        embed.add_field(

            name="На игрока",

            value=self.player.value,

            inline=False

        )


        embed.add_field(

            name="Причина",

            value=self.reason.value,

            inline=False

        )


        await channel.send(

            embed=embed,

            view=CloseView(member.id)

        )


        await interaction.response.send_message(

            "✅ Жалоба отправлена",

            ephemeral=True

        )



# ================= REPORT BUTTON =================


class ReportView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )


    @discord.ui.button(

        label="Подать жалобу",

        style=discord.ButtonStyle.danger,

        custom_id="create_report"

    )

    async def report(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        await interaction.response.send_modal(

            ReportForm()

        )



# ================= COG =================


class Reports(commands.Cog):


    def __init__(self, bot):

        self.bot = bot



    @app_commands.command(

        name="reportplayer",

        description="Отправить панель жалоб"

    )

    async def reportplayer(

        self,

        interaction: discord.Interaction

    ):


        embed = discord.Embed(

            title="⚠️ Жалобы",

            description="Нажмите кнопку ниже для подачи жалобы."

        )


        await interaction.channel.send(

            embed=embed,

            view=ReportView()

        )


        await interaction.response.send_message(

            "✅ Панель жалоб отправлена",

            ephemeral=True

        )



async def setup(bot):

    await bot.add_cog(

        Reports(bot)

    )