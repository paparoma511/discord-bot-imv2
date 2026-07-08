import discord


from config import CATEGORY_APPLICATIONS, ADMIN_ROLE_IDS

from views.admin_buttons import AdminView

from database.database import add_application



QUESTIONS = {


    "NORULES": [

        "Возраст",

        "Ник",

        "SteamID",

        "Сколько часов в SCP:SL?",

        "Расскажите о себе"

    ],



    "EVENTS": [

        "Возраст",

        "Ник",

        "Какие ивенты хотите проводить?",

        "Есть ли опыт проведения ивентов?",

        "Расскажите о себе"

    ],



    "DISCORD": [

        "Возраст",

        "Ник",

        "Когда создали Discord аккаунт?",

        "Был ли у вас опыт работы Discord модератором?",

        "Расскажите о себе"

    ]

}



class DepartmentForm(discord.ui.Modal):


    def __init__(self, department):


        super().__init__(

            title=f"Заявка {department}"

        )


        self.department = department


        self.inputs = []



        for question in QUESTIONS[department]:


            field = discord.ui.TextInput(

                label=question,

                style=discord.TextStyle.long

                if "Расскажите" in question

                else discord.TextStyle.short

            )


            self.inputs.append(field)

            self.add_item(field)




    async def on_submit(self, interaction):


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

            )

        }



        for role_id in ADMIN_ROLE_IDS:


            role = guild.get_role(role_id)


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

            title=f"Заявка {self.department}"

        )


        embed.add_field(

            name="Игрок",

            value=member.mention,

            inline=False

        )



        for field in self.inputs:


            embed.add_field(

                name=field.label,

                value=field.value,

                inline=False

            )



        await channel.send(

            embed=embed,

            view=AdminView(member.id)

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