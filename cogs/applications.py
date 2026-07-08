import discord

from discord.ext import commands

from discord import app_commands


from views.application_buttons import ApplicationView

from utils.permissions import is_admin

from utils.slots import get_department_slots



class Applications(commands.Cog):


    def __init__(self, bot):

        self.bot = bot




    @app_commands.command(

        name="application",

        description="Создать панель заявок"

    )

    async def application(

        self,

        interaction: discord.Interaction

    ):


        if not is_admin(interaction.user):

            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )



        embed = discord.Embed(

            title="📋 Набор в отделы",

            description=(

                "Выберите отдел:\n\n"

                f"{get_department_slots(interaction.guild)}"

                "\nУсловия:\n"

                "• Возраст от 13 лет\n"

                "• Знание правил\n"

                "• Активность\n"

            )

        )



        await interaction.channel.send(

            embed=embed,

            view=ApplicationView()

        )



        await interaction.response.send_message(

            "✅ Панель отправлена",

            ephemeral=True

        )





async def setup(bot):

    await bot.add_cog(

        Applications(bot)

    )