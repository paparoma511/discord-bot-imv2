import discord

from modals.application_form import DepartmentForm



class ApplicationView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )



    @discord.ui.button(

        label="NORULES",

        style=discord.ButtonStyle.primary,

        custom_id="application_norules"

    )

    async def norules(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        await interaction.response.send_modal(

            DepartmentForm(
                "NORULES"
            )

        )



    @discord.ui.button(

        label="EVENTS",

        style=discord.ButtonStyle.success,

        custom_id="application_events"

    )

    async def events(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        await interaction.response.send_modal(

            DepartmentForm(
                "EVENTS"
            )

        )



    @discord.ui.button(

        label="DISCORD",

        style=discord.ButtonStyle.secondary,

        custom_id="application_discord"

    )

    async def discord_department(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        await interaction.response.send_modal(

            DepartmentForm(
                "DISCORD"
            )

        )