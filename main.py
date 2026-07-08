# ================= CONFIG =================


# Каналы

APPLICATION_CHANNEL_ID = 1463831540386627635

REPORT_CHANNEL_ID = 1463832239400816695


# Категории для тикетов

CATEGORY_APPLICATIONS = 1474492852259262464

CATEGORY_REPORTS = 1474492852259262464


# Логи

LOG_CHANNEL_ID = 1498669547484348467



# ================= ADMIN =================


# Главная администрация бота

ADMIN_ROLE_IDS = [

    1474489466952351987,
    1501898065248915506,
    1513631902966354111

]



# ================= DEPARTMENTS =================


# Администрация сервера

NORULES = [

    111111111111,
    222222222222

]


# Ивент отдел

EVENTS = [

    333333333333,
    444444444444

]


# Discord отдел

DISCORD = [

    555555555555,
    666666666666

]



# ================= LIMITS =================


# Максимальное количество сотрудников


NORULES_SLOTS = 5


EVENTS_SLOTS = 3


DISCORD_SLOTS = 2



# ================= BOT SETTINGS =================


BOT_NAME = "IMPERIAL || Project"


TICKET_PREFIX = "заявка"

# ================= BOT =================

import os
import asyncio
from datetime import timedelta

import discord
from discord.ext import commands
from discord import app_commands



intents = discord.Intents.default()

intents.message_content = True
intents.members = True



bot = commands.Bot(
    command_prefix="!",
    intents=intents
)



# ================= PERMISSIONS =================


def is_admin(member: discord.Member):

    return any(
        role.id in ADMIN_ROLE_IDS
        for role in member.roles
    )



# ================= SLOTS =================


def get_department_slots(guild):

    departments = {

        "NORULES": {
            "roles": NORULES,
            "slots": NORULES_SLOTS
        },

        "EVENTS": {
            "roles": EVENTS,
            "slots": EVENTS_SLOTS
        },

        "DISCORD": {
            "roles": DISCORD,
            "slots": DISCORD_SLOTS
        }

    }


    text = ""


    for name, data in departments.items():

        count = 0


        for member in guild.members:

            for role in member.roles:

                if role.id in data["roles"]:

                    count += 1
                    break


        free = data["slots"] - count

        if free < 0:
            free = 0


        text += (
            f"**{name}**\n"
            f"👥 Занято: `{count}/{data['slots']}`\n"
            f"🟢 Свободно: `{free}`\n\n"
        )


    return text

# ================= LOG =================


async def log(text):

    try:

        channel = await bot.fetch_channel(
            LOG_CHANNEL_ID
        )

        await channel.send(
            f"ℹ️ LOGGER\n{text}"
        )


    except:

        pass

# ================= REASON MODAL =================


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



    async def on_submit(self, interaction):

        if not is_admin(interaction.user):

            return await interaction.response.send_message(
                "❌ Нет прав",
                ephemeral=True
            )


        if self.action == "approve":

            await self.user.send(
                f"🎉 Ваша заявка принята!\n"
                f"Комментарий: {self.reason.value}"
            )


        else:

            await self.user.send(
                f"❌ Ваша заявка отклонена!\n"
                f"Причина: {self.reason.value}"
            )


        await interaction.response.send_message(
            "Готово",
            ephemeral=True
        )


        await asyncio.sleep(3)

        await interaction.channel.delete()

# ================= ADMIN VIEW =================


class AdminView(discord.ui.View):

    def __init__(self, user_id):

        super().__init__(
            timeout=None
        )

        self.user_id = user_id



    @discord.ui.button(
        label="Взять",
        style=discord.ButtonStyle.blurple,
        custom_id="take_ticket"
    )

    async def take(self, interaction, button):

        if not is_admin(interaction.user):

            return await interaction.response.send_message(
                "❌ Нет прав",
                ephemeral=True
            )


        await interaction.response.send_message(
            "✅ Заявка взята",
            ephemeral=True
        )



    @discord.ui.button(
        label="Принять",
        style=discord.ButtonStyle.success,
        custom_id="approve_ticket"
    )

    async def approve(self, interaction, button):

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
        label="Отказать",
        style=discord.ButtonStyle.danger,
        custom_id="reject_ticket"
    )

    async def reject(self, interaction, button):

        user = interaction.guild.get_member(
            self.user_id
        )


        await interaction.response.send_modal(
            ReasonModal(
                user,
                "reject"
            )
        )

# ================= CLOSE VIEW =================


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

    async def close(self, interaction, button):

        if (

            interaction.user.id != self.owner_id

            and not is_admin(interaction.user)

        ):

            return await interaction.response.send_message(
                "❌ Нет прав",
                ephemeral=True
            )


        await interaction.response.send_message(
            "Закрываю..."
        )


        await asyncio.sleep(3)

        await interaction.channel.delete()

# ================= APPLICATION FORM =================


class DepartmentForm(discord.ui.Modal):

    def __init__(self, department):

        super().__init__(
            title=department
        )

        self.department = department


        self.age = discord.ui.TextInput(
            label="Возраст"
        )

        self.nick = discord.ui.TextInput(
            label="Ник"
        )

        self.steam = discord.ui.TextInput(
            label="SteamID"
        )

        self.about = discord.ui.TextInput(
            label="О себе",
            style=discord.TextStyle.long
        )


        for x in [
            self.age,
            self.nick,
            self.steam,
            self.about
        ]:

            self.add_item(x)



    async def on_submit(self, interaction):

        await create_ticket(
            interaction,
            self.department,
            self
        )
async def create_ticket(
    interaction,
    department,
    form
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
        )

    }


    for role_id in ADMIN_ROLE_IDS:

        role = guild.get_role(role_id)

        if role:

            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True
            )


    channel = await guild.create_text_channel(

        f"{department.lower()}-{member.name}",

        category=category,

        overwrites=overwrites

    )


    embed = discord.Embed(
        title=f"Заявка {department}"
    )


    embed.add_field(
        name="Игрок",
        value=member.mention
    )

    embed.add_field(
        name="Возраст",
        value=form.age.value
    )

    embed.add_field(
        name="Ник",
        value=form.nick.value
    )

    embed.add_field(
        name="SteamID",
        value=form.steam.value
    )

    embed.add_field(
        name="О себе",
        value=form.about.value
    )


    await channel.send(
        embed=embed,
        view=AdminView(member.id)
    )


    await interaction.response.send_message(
        "✅ Заявка создана",
        ephemeral=True
    )

class ApplicationView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="NORULES",
        style=discord.ButtonStyle.primary,
        custom_id="norules"
    )

    async def norules(self, interaction, button):

        await interaction.response.send_modal(
            DepartmentForm("NORULES")
        )



    @discord.ui.button(
        label="EVENTS",
        style=discord.ButtonStyle.success,
        custom_id="events"
    )

    async def events(self, interaction, button):

        await interaction.response.send_modal(
            DepartmentForm("EVENTS")
        )



    @discord.ui.button(
        label="DISCORD",
        style=discord.ButtonStyle.secondary,
        custom_id="discord"
    )

    async def discord_dep(self, interaction, button):

        await interaction.response.send_modal(
            DepartmentForm("DISCORD")
        )

@bot.event
async def on_ready():


    bot.add_view(
        ApplicationView()
    )


    bot.add_view(
        CloseView(0)
    )


    bot.add_view(
        AdminView(0)
    )


    await bot.tree.sync()


    print(
        f"ONLINE {bot.user}"
    )



TOKEN = os.getenv(
    "BOT_TOKEN"
)


bot.run(
    TOKEN
)
