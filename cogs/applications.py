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

                "\n⚠️Условия при которых ваша заявка будет одобрена⚠️\n"

                "• Вам должно быть 13 лет минимум\n"

                "• Вы должны знать правила сервера\n"

                "• Вы должны наиграть на сервере не менее 5 часов\n"
               
                "• У вас должен быть открытый Steam аккаунт\n"

                "• У вас должно быть наигранно минимум 50 часов в SCP:SL\n"

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