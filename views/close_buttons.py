import asyncio

import discord

from utils.permissions import is_admin

from utils.logger import log



class CloseView(discord.ui.View):


    def __init__(self, owner_id):

        super().__init__(
            timeout=None
        )

        self.owner_id = owner_id



    @discord.ui.button(

        label="Закрыть",

        style=discord.ButtonStyle.danger,

        custom_id="close_ticket"

    )

    async def close(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        if (

            interaction.user.id != self.owner_id

            and not is_admin(interaction.user)

        ):


            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )



        await interaction.response.send_message(

            "🔒 Закрываю тикет..."

        )


        await log(

            interaction.client,

            f"Закрыт тикет {interaction.channel.name}"

        )


        await asyncio.sleep(3)


        await interaction.channel.delete()