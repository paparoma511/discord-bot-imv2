print("FILE STARTED")

import os
import asyncio
from datetime import timedelta

import discord
from discord.ext import commands
from discord import app_commands

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
        await ch.send(f"[ℹ️] LOGGER: {text}")
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
                await self.user.send(f"🎉 **Ваша заявка на сервере IMPERIAL || Project ПРИНЯТА!**\n**Комментарий:** {self.reason.value}")
                await interaction.channel.send("Принято")
                await log(f"Заявка принята {self.user}")

            else:
                await self.user.send(f"❌ **Ваша заявка на сервере IMPERIAL || Project ОТКЛОНЕНА.**\n**Причина:** {self.reason.value}")
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

        await interaction.response.send_message("Вы взяли заявку на рассмотрение заявка на рассмотрение", ephemeral=True)

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
        self.hours = discord.ui.TextInput(label="Сколько вы наиграли часов в игре?")
        self.about = discord.ui.TextInput(label="Расскажите о себе", style=discord.TextStyle.long)

        self.add_item(self.nick)
        self.add_item(self.steamid)
        self.add_item(self.steamlink)
        self.add_item(self.hours)
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
            name=f"【⚠️】заявка-{member.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(title="Новая заявка")
        embed.add_field(name="Игрок", value=member.mention, inline=False)
        embed.add_field(name="Ник", value=self.nick.value, inline=False)
        embed.add_field(name="SteamID", value=self.steamid.value, inline=False)
        embed.add_field(name="Ссылка на Steam аккаунт", value=self.steamlink.value, inline=False)
        embed.add_field(name="Часов в игре", value=self.hours.value, inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)

        await channel.send(embed=embed, view=AdminView(member.id))

        await log(f"Новая заявка: {member}")


class ReportForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Жалоба")

        self.target = discord.ui.TextInput(label="Никнейм нарушителя")
        self.yesorno = discord.ui.TextInput(label="Игрок администратор? (Да/нет)")
        self.reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.long)

        self.add_item(self.target)
        self.add_item(self.yesorno)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_REPORTS)

        channel = await guild.create_text_channel(
            name=f"【⚠️】жалоба-{member.name}",
            category=category
        )

        embed = discord.Embed(title="Новая жалоба")
        embed.add_field(name="От", value=member.mention, inline=False)
        embed.add_field(name="На", value=self.target.value, inline=False)
        embed.add_field(name="Был ли игрок администратором", value=self.yesorno.value, inline-False)
        embed.add_field(name="Причина", value=self.reason.value, inline=False)

        await channel.send(embed=embed, view=CloseView(member.id))
        await log(f"Жалоба: {member} на {self.target.value}")

        await interaction.response.send_message("Жалоба отправлена", ephemeral=True)


# ================= MAIN PANEL =================

class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Подать заявку в администрацию",
        style=discord.ButtonStyle.success
    )
    async def app(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationForm())


class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пожаловаться на игрока/администратора",
        style=discord.ButtonStyle.danger
    )
    async def rep(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportForm())


# ================= ON READY =================

@bot.event
async def on_ready():
    print("ON_READY CALLED")

    try:
        synced = await bot.tree.sync()
        print(f"SYNCED: {len(synced)}")

        for cmd in synced:
            print(f"COMMAND: /{cmd.name}")

    except Exception as e:
        print(f"SYNC ERROR: {e}")

    print(f"BOT ONLINE: {bot.user}")

@bot.tree.command(
    name="application",
    description="Отправить панель подачи заявки"
)
async def application(interaction: discord.Interaction):

    if not is_admin(interaction.user):
        return await interaction.response.send_message(
            "❌ Нет прав",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Подача заявки в администрацию",
        description=(
            "Условия при которых ваша заявка будет одобрена:\n"
            "• вам должно быть не меньше 13 лет\n"
            "• вы должны знать правила сервера\n"
            "• у вас должно быть наигранно не менее 50 часов в SCP:SL\n"
            "• у вас должен быть открытый Steam аккаунт\n"
            "-----------------------------\n"
            "Без этого ваша заявка будет автоматически отклонена\n"
            "⚠️ Шуточные заявки будут отклоняться. Кто подавал шуточную заявку получит наказание на усмотрение высшей администрации ⚠️"
        )
    )

    await interaction.channel.send(
        embed=embed,
        view=ApplicationView()
    )

    await interaction.response.send_message(
        "✅ Панель заявок отправлена",
        ephemeral=True
    )


@bot.tree.command(
    name="reportplayer",
    description="Отправить панель жалоб"
)
async def reportplayer(interaction: discord.Interaction):

    if not is_admin(interaction.user):
        return await interaction.response.send_message(
            "❌ Нет прав",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Подача жалобы",
        description="Нажмите кнопку ниже для подачи жалобы."
    )

    await interaction.channel.send(
        embed=embed,
        view=ReportView()
    )

    await interaction.response.send_message(
        "✅ Панель жалоб отправлена",
        ephemeral=True
    )

@bot.tree.command(
    name="mute",
    description="Замутить участника"
)
@app_commands.describe(
    player="Игрок",
    duration="Время в минутах",
    reason="Причина мута"
)
async def mute(
    interaction: discord.Interaction,
    player: discord.Member,
    duration: int,
    reason: str
):

    if not is_admin(interaction.user):
        return await interaction.response.send_message(
            "❌ Нет прав",
            ephemeral=True
        )

    try:
        until = discord.utils.utcnow() + timedelta(minutes=duration)

        await player.timeout(
            until,
            reason=f"{interaction.user} | {reason}"
        )

        embed = discord.Embed(
            title="🔇 Участник замучен",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Игрок",
            value=player.mention,
            inline=False
        )

        embed.add_field(
            name="Срок",
            value=f"{duration} мин.",
            inline=False
        )

        embed.add_field(
            name="Причина",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="Модератор",
            value=interaction.user.mention,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        try:
            await player.send(
                f"🔇 Вы получили мут на сервере **{interaction.guild.name}**\n"
                f"⏳ Срок: {duration} мин.\n"
                f"📝 Причина: {reason}"
            )
        except:
            pass

        await log(
            f"MUTE | {player} | {duration} мин | {reason} | {interaction.user}"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Ошибка: {e}",
            ephemeral=True
        )

@bot.tree.command(
    name="unmute",
    description="Снять мут с участника"
)
@app_commands.describe(
    player="Игрок"
)
async def unmute(
    interaction: discord.Interaction,
    player: discord.Member
):

    if not is_admin(interaction.user):
        return await interaction.response.send_message(
            "❌ Нет прав",
            ephemeral=True
        )

    try:
        await player.timeout(None)

        await interaction.response.send_message(
            f"✅ Мут снят с {player.mention}"
        )

        await log(
            f"UNMUTE | {player} | {interaction.user}"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Ошибка: {e}",
            ephemeral=True
        )


# ================= RUN =================

TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)
