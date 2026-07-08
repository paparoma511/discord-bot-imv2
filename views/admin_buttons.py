import discord

from modals.reason_form import ReasonModal

from utils.permissions import is_admin



class AdminView(discord.ui.View):


    def __init__(self, user_id):

        super().__init__(
            timeout=None
        )

        self.user_id = user_id




    @discord.ui.button(

        label="Взять на рассмотрение",

        style=discord.ButtonStyle.blurple,

        custom_id="take_application"

    )

    async def take(

        self,

        interaction,

        button

    ):


        if not is_admin(interaction.user):

            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )


        await interaction.response.send_message(

            "✅ Заявка взята на рассмотрение",

            ephemeral=True

        )





    @discord.ui.button(

        label="Принять",

        style=discord.ButtonStyle.success,

        custom_id="approve_application"

    )

    async def approve(

        self,

        interaction,

        button

    ):


        user = interaction.guild.get_member(

            self.user_id

        )


        await interaction.response.send_modal(

            ReasonModal(

                user,

                "approve"

            )

        )





    @discord.ui.button(

        label="Отклонить",

        style=discord.ButtonStyle.danger,

        custom_id="reject_application"

    )

    async def reject(

        self,

        interaction,

        button

    ):


        user = interaction.guild.get_member(

            self.user_id

        )


        await interaction.response.send_modal(

            ReasonModal(

                user,

                "reject"

            )

        )