import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================

APPLICATION_CHANNEL_ID = 1463831540386627635
SECOND_APPLICATION_CHANNEL_ID = 1463832239400816695
CATEGORY_ID = 1474492852259262464

ADMIN_ROLE_IDS = [
    1474489466952351987,
    1501898065248915506,
    1513631902966354111
]

MAIN_MESSAGE_TITLE = "Подача заявки"
MAIN_MESSAGE_DESCRIPTION = "Нажмите кнопку ниже чтобы подать заявку"

FORM_TITLE = "Заявка"

# ================= BOT =================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def has_admin_role(member: discord.Member):
    return any(role.id in ADMIN_ROLE_IDS for role in member.roles)


# ================= CLOSE TICKET =================

class CloseTicketView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.owner_id and not has_admin_role(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        await interaction.response.send_message("Закрываю...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()


# ================= REASON =================

class ReasonModal(discord.ui.Modal):
    def __init__(self, action, user):
        super().__init__(title="Причина")
        self.action = action
        self.user = user

        self.reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.long)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        try:
            if self.action == "approve":
                await self.user.send(f"✅ Принят: {self.reason.value}")
                await interaction.channel.send("Принято")
            else:
                await self.user.send(f"❌ Отклонён: {self.reason.value}")
                await interaction.channel.send("Отклонено")

            await asyncio.sleep(3)
            await interaction.channel.delete()

        except:
            await interaction.channel.send("❌ Не удалось отправить ЛС")


# ================= ADMIN PANEL =================

class AdminView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Взять", style=discord.ButtonStyle.blurple)
    async def take(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        user = interaction.guild.get_member(self.user_id)
        if user:
            await user.send("👀 Взято в работу")

        await interaction.response.send_message("OK", ephemeral=True)

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.guild.get_member(self.user_id)
        await interaction.response.send_modal(ReasonModal("approve", user))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.guild.get_member(self.user_id)
        await interaction.response.send_modal(ReasonModal("reject", user))


# ================= FORM =================

class Form(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)

        self.nick = discord.ui.TextInput(label="Ник")
        self.steam = discord.ui.TextInput(label="SteamID")
        self.about = discord.ui.TextInput(label="О себе", style=discord.TextStyle.long)

        self.add_item(self.nick)
        self.add_item(self.steam)
        self.add_item(self.about)

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }

        for r in ADMIN_ROLE_IDS:
            role = guild.get_role(r)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        channel = await guild.create_text_channel(
            name=f"заявка-{member.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(title="Новая заявка")
        embed.add_field(name="Игрок", value=member.mention, inline=False)
        embed.add_field(name="Ник", value=self.nick.value, inline=False)
        embed.add_field(name="Steam", value=self.steam.value, inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)

        await channel.send(embed=embed, view=AdminView(member.id))
        await channel.send(view=CloseTicketView(member.id))

        await interaction.response.send_message(f"Создано: {channel.mention}", ephemeral=True)


# ================= BUTTON =================

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.success)
    async def btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Form())


# ================= START =================

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")

    embed = discord.Embed(
        title=MAIN_MESSAGE_TITLE,
        description=MAIN_MESSAGE_DESCRIPTION
    )

    ch1 = bot.get_channel(APPLICATION_CHANNEL_ID)
    if ch1:
        await ch1.send(embed=embed, view=MainView())

    ch2 = bot.get_channel(SECOND_APPLICATION_CHANNEL_ID)
    if ch2:
        await ch2.send(embed=embed, view=MainView())


TOKEN = os.getenv("BOT_TOKEN")

bot.run(TOKEN)