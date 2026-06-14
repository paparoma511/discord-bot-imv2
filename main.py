import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================

APPLICATION_CHANNEL_ID = 1463831540386627635
REPORT_CHANNEL_ID = 1463832239400816695

CATEGORY_APPLICATIONS = 1474492852259262464
CATEGORY_REPORTS = 1474492852259262464

LOG_CHANNEL_ID = 1498669547484348467

ADMIN_ROLE_IDS = [1474489466952351987, 1501898065248915506, 1513631902966354111]

# ================= BOT =================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def is_admin(member: discord.Member):
    return any(r.id in ADMIN_ROLE_IDS for r in member.roles)


# ================= LOG =================

async def log(text: str):
    try:
        ch = await bot.fetch_channel(LOG_CHANNEL_ID)
        await ch.send(f"📌 LOG:\n{text}")
    except:
        pass


# ================= CLOSE TICKET =================

class CloseView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(label="Закрыть", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.owner_id and not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        await interaction.response.send_message("Закрытие...", ephemeral=True)
        await log(f"Тикет закрыт: {interaction.channel.name}")
        await asyncio.sleep(5)
        await interaction.channel.delete()


# ================= REASON =================

class ReasonModal(discord.ui.Modal):
    def __init__(self, user, action):
        super().__init__(title="Причина")
        self.user = user
        self.action = action

        self.reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.long)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):

        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        try:
            if self.action == "approve":
                await self.user.send(f"🎉 **Ваша заявка на сервере IMPERIAL || Project ПРИНЯТА!**\n**Комментарий:{self.reason.value}**")
                await interaction.channel.send("Принято")
                await log(f"Заявка принята {self.user}")

            else:
                await self.user.send(f"❌ **Ваша заявка на сервере IMPERIAL || Project ОТКЛОНЕНА.**\n**Причина:{self.reason.value}**")
                await interaction.channel.send("Отклонено")
                await log(f"Заявка отклонена {self.user}")

            await asyncio.sleep(3)
            await interaction.channel.delete()

        except:
            await interaction.channel.send("❌ ЛС закрыты")


# ================= ADMIN PANEL =================

class AdminView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Взять на рассмотрение", style=discord.ButtonStyle.blurple)
    async def take(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        user = interaction.guild.get_member(self.user_id)
        if user:
            await user.send("👀 **Ваша заявка на сервере IMPERIAL || Project взята на рассмотрение администрацией!**")

        await interaction.response.send_message("Ваша заявка взята на рассмотрение", ephemeral=True)

    @discord.ui.button(label="Принять заявку", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.guild.get_member(self.user_id)
        await interaction.response.send_modal(ReasonModal(user, "approve"))

    @discord.ui.button(label="Отклонить заявку", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.guild.get_member(self.user_id)
        await interaction.response.send_modal(ReasonModal(user, "reject"))


# ================= FORMS =================

class ApplicationForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Заявка")

        self.nick = discord.ui.TextInput(label="Ваш никнейм")
        self.steamid = discord.ui.TextInput(label="Ваш SteamID")
        self.steamlink = discord.ui.TextInput(label="Ссылка на ваш Steam аккаунт")
        self.about = discord.ui.TextInput(label="Расскажите о себе", style=discord.TextStyle.long)

        self.add_item(self.nick)
        self.add_item(self.steamid)
        self.add_item(self.steamlink)
        self.add_item(self.about)

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_APPLICATIONS)

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
        embed.add_field(name="SteamID", value=self.steamid.value, inline=False)
        embed.add_field(name="Ссылка на Steam аккаунт", value=self.steamlink.value, inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)

        await channel.send(embed=embed, view=AdminView(member.id))
        await channel.send(view=CloseView(member.id))

        await log(f"Новая заявка: {member}")


class ReportForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Жалоба")

        self.target = discord.ui.TextInput(label="На кого жалоба")
        self.reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.long)

        self.add_item(self.target)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_REPORTS)

        channel = await guild.create_text_channel(
            name=f"жалоба-{member.name}",
            category=category
        )

        embed = discord.Embed(title="Новая жалоба")
        embed.add_field(name="От", value=member.mention, inline=False)
        embed.add_field(name="На", value=self.target.value, inline=False)
        embed.add_field(name="Причина", value=self.reason.value, inline=False)

        await channel.send(embed=embed, view=CloseView(member.id))
        await log(f"Жалоба: {member} на {self.target.value}")

        await interaction.response.send_message("Жалоба отправлена", ephemeral=True)


# ================= MAIN PANEL =================

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Подать заявку в администрацию", style=discord.ButtonStyle.success)
    async def app(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationForm())

    @discord.ui.button(label="Пожаловаться на игрока/администратора", style=discord.ButtonStyle.danger)
    async def rep(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportForm())


# ================= ON READY =================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    embed = discord.Embed(
        title="Подача заявки в администрацию и подача жалобы на игрока/администратора",
        description="Условия при которых ваша заявка на администраторп будет принята\n- вам должно быть не меньше 13 лет\n- вы должны знать правила сервера\n- вы должны знать регламент администрации сервера\n- у вас должно быть наигранно не менее 50 часов в SCP:SL\n-----------------------------\n⚠️Шуточные заявки будут отклоняться ⚠️"
    )

    ch1 = await bot.fetch_channel(APPLICATION_CHANNEL_ID)
    await ch1.send(embed=embed, view=MainView())

    ch2 = await bot.fetch_channel(REPORT_CHANNEL_ID)
    await ch2.send(embed=embed, view=MainView())


# ================= RUN =================

TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)