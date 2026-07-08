import asyncio

import discord

from utils.permissions import is_admin

from utils.logger import log



class ReasonModal(discord.ui.Modal):


    def __init__(self, user, action):

        super().__init__(
            title="Причина"
        )


        self.user = user

        self.action = action



        self.reason = discord.ui.TextInput(

            label="Причина",

            style=discord.TextStyle.long

        )


        self.add_item(
            self.reason
        )



    async def on_submit(

        self,

        interaction: discord.Interaction

    ):


        if not is_admin(interaction.user):


            return await interaction.response.send_message(

                "❌ Нет прав",

                ephemeral=True

            )



        text = self.reason.value



        try:


            if self.action == "approve":


                await self.user.send(

                    "🎉 Ваша заявка принята!\n\n"

                    f"Комментарий:\n{text}"

                )


                await log(

                    interaction.client,

                    f"Заявка принята: {self.user}"

                )



            else:


                await self.user.send(

                    "❌ Ваша заявка отклонена!\n\n"

                    f"Причина:\n{text}"

                )


                await log(

                    interaction.client,

                    f"Заявка отклонена: {self.user}"

                )



        except:


            pass




        await interaction.response.send_message(

            "✅ Выполнено",

            ephemeral=True

        )



        await asyncio.sleep(3)



        await interaction.channel.delete()