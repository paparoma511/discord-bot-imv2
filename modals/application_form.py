import discord


from config import (

    CATEGORY_APPLICATIONS,

    ADMIN_ROLE_IDS

)


from views.admin_buttons import AdminView


from database.database import add_application



class DepartmentForm(discord.ui.Modal):


    def __init__(self, department):


        super().__init__(

            title=f"Заявка {department}"

        )


        self.department = department



        self.age = discord.ui.TextInput(

            label="Ваш возраст"

        )


        self.nick = discord.ui.TextInput(

            label="Ваш ник"

        )


        self.steam = discord.ui.TextInput(

            label="Ваш SteamID"

        )


        self.about = discord.ui.TextInput(

            label="Расскажите о себе",

            style=discord.TextStyle.long

        )



        self.add_item(self.age)

        self.add_item(self.nick)

        self.add_item(self.steam)

        self.add_item(self.about)




    async def on_submit(

        self,

        interaction: discord.Interaction

    ):


        guild = interaction.guild

        member = interaction.user



        category = discord.utils.get(

            guild.categories,

            id=CATEGORY_APPLICATIONS

        )



        overwrites = {



            guild.default_role:

            discord.PermissionOverwrite(

                read_messages=False

            ),



            member:

            discord.PermissionOverwrite(

                read_messages=True

            ),



            guild.me:

            discord.PermissionOverwrite(

                read_messages=True

            )

        }




        for role_id in ADMIN_ROLE_IDS:


            role = guild.get_role(

                role_id

            )


            if role:


                overwrites[role] = discord.PermissionOverwrite(

                    read_messages=True

                )





        channel = await guild.create_text_channel(


            name=f"{self.department.lower()}-{member.name}",


            category=category,


            overwrites=overwrites


        )





        embed = discord.Embed(

            title=f"Новая заявка | {self.department}"

        )



        embed.add_field(

            name="Игрок",

            value=member.mention,

            inline=False

        )



        embed.add_field(

            name="Возраст",

            value=self.age.value

        )


        embed.add_field(

            name="Ник",

            value=self.nick.value

        )


        embed.add_field(

            name="SteamID",

            value=self.steam.value

        )


        embed.add_field(

            name="О себе",

            value=self.about.value,

            inline=False

        )





        await channel.send(

            embed=embed,

            view=AdminView(

                member.id

            )

        )



        await add_application(

            member.id,

            self.department,

            channel.id

        )




        await interaction.response.send_message(

            "✅ Заявка создана",

            ephemeral=True

        )