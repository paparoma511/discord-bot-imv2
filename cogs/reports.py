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



    async def on_submit(self, interaction):


        guild = interaction.guild

        member = interaction.user



        channel = await guild.create_text_channel(

            name=f"жалоба-{member.name}"

        )



        embed = discord.Embed(

            title="Новая жалоба"

        )



        embed.add_field(

            name="От",

            value=member.mention

        )


        embed.add_field(

            name="На",

            value=self.player.value

        )


        embed.add_field(

            name="Причина",

            value=self.reason.value

        )



        await channel.send(

            embed=embed,

            view=CloseView(member.id)

        )



        await interaction.response.send_message(

            "✅ Жалоба отправлена",

            ephemeral=True

        )





class Reports(commands.Cog):


    def __init__(self, bot):

        self.bot = bot




    @app_commands.command(

        name="reportplayer",

        description="Создать панель жалоб"

    )

    async def reportplayer(self, interaction):


        embed = discord.Embed(

            title="⚠️ Жалобы",

            description="Нажмите кнопку ниже"

        )


        view = discord.ui.View(timeout=None)



        @view.button(

            label="Подать жалобу",

            style=discord.ButtonStyle.danger,

            custom_id="report_button"

        )

        async def report(

            button_interaction,

            button

        ):


            await button_interaction.response.send_modal(

                ReportForm()

            )



        await interaction.channel.send(

            embed=embed,

            view=view

        )


        await interaction.response.send_message(

            "Готово",

            ephemeral=True

        )





async def setup(bot):

    await bot.add_cog(

        Reports(bot)

    )