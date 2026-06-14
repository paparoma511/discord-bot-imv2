import os
import asyncio
import discord
from discord.ext import commands

# ==================== НАСТРОЙКА ====================

APPLICATION_CHANNEL_ID = 1463831540386627635
SECOND_APPLICATION_CHANNEL_ID = 1463832239400816695
CATEGORY_ID = 1474492852259262464

ADMIN_ROLE_IDS = [
    1474489466952351987,
    1501898065248915506,
    1513631902966354111
]

MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера NORULES"
MAIN_MESSAGE_DESCRIPTION = (
    "Условия:\n"
    "- 13+ лет\n"
    "- знание правил\n"
    "- 50+ часов SCP:SL\n"
    "⚠️ Шутки = наказание"
)

FORM_TITLE = "Подать заявку"

# ==================== BOT ====================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def has_admin_role(user: discord.Member) -> bool:
    return any(role.id in ADMIN_ROLE_IDS for role in user.roles)


# ==================== CLOSE TICKET ====================

class CloseTicketView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(
        label="Закрыть тикет",
        style=discord.ButtonStyle.danger
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        member = interaction.user
        is_admin = has_admin_role(member)
        is_owner = member.id == self.owner_id

        if not is_admin and not is_owner:
            return await interaction.response.send_message(
                "❌ Нет прав",
                ephemeral=True
            )

        await interaction.response.send_message("🔒 Закрытие...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()


# ==================== REASON MODAL ====================

class ReasonModal(discord.ui.Modal):
    def __init__(self, action_type: str, candidate: discord.Member):
        super().__init__(title="Причина")
        self.action_type = action_type
        self.candidate = candidate

        self.reason = discord.ui.TextInput(
            label="Причина",
            style=discord.TextStyle.long,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not has_admin_role(interaction.user):
            return await interaction.followup.send("❌ Нет прав", ephemeral=True)

        try:
            if self.action_type == "approve":
                await self.candidate.send(
                    f"🎉 Заявка ПРИНЯТА!\n{self.reason.value}"
                )
                await interaction.channel.send("✅ Принято")
            else:
                await self.candidate.send(
                    f"❌ Заявка ОТКЛОНЕНА!\n{self.reason.value}"
                )
                await interaction.channel.send("❌ Отклонено")

            await asyncio.sleep(5)
            await interaction.channel.delete()

        except discord.Forbidden:
            await interaction.channel.send("⚠️ ЛС закрыты")


# ==================== ADMIN PANEL ====================

class AdminTicketView(discord.ui.View):
    def __init__(self, candidate_id: int):
        super().__init__(timeout=None)
        self.candidate_id = candidate_id

    @discord.ui.button(label="Взять", style=discord.ButtonStyle.blurple)
    async def review(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("❌ Нет прав", ephemeral=True)

        candidate = interaction.guild.get_member(self.candidate_id)
        if not candidate:
            return await interaction.response.send_message("❌ Нет кандидата", ephemeral=True)

        await candidate.send("👀 Ваша заявка на рассмотрении")
        await interaction.response.send_message("⚙️ Взято", ephemeral=True)

        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidate = interaction.guild.get_member(self.candidate_id)
        await interaction.response.send_modal(ReasonModal("approve", candidate))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidate = interaction.guild.get_member(self.candidate_id)
        await interaction.response.send_modal(ReasonModal("reject", candidate))


# ==================== FORM ====================

class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)

        self.name = discord.ui.TextInput(label="Ник")
        self.steamid = discord.ui.TextInput(label="SteamID")
        self.linksteam = discord.ui.TextInput(label="Steam ссылка")
        self.experience = discord.ui.TextInput(label="Опыт?")
        self.about = discord.ui.TextInput(label="О себе", style=discord.TextStyle.long)

        self.add_item(self.name)
        self.add_item(self.steamid)
        self.add_item(self.linksteam)
        self.add_item(self.experience)
        self.add_item(self.about)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        if not category:
            return await interaction.followup.send("❌ Нет категории", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }

        for role_id in ADMIN_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        channel = await guild.create_text_channel(
            name=f"заявка-{member.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(title="Новая заявка")
        embed.add_field(name="Игрок", value=member.mention, inline=False)
        embed.add_field(name="Ник", value=self.name.value, inline=False)
        embed.add_field(name="SteamID", value=self.steamid.value, inline=False)
        embed.add_field(name="Ссылка", value=self.linksteam.value, inline=False)
        embed.add_field(name="Опыт", value=self.experience.value, inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)

        await channel.send(embed=embed, view=AdminTicketView(member.id))

        await channel.send(
            content="🔒 Закрыть тикет:",
            view=CloseTicketView(member.id)
        )

        await interaction.followup.send(f"✅ Создано: {channel.mention}", ephemeral=True)


# ==================== BUTTON ====================

class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Подать заявку",
        style=discord.ButtonStyle.success
    )
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())


# ==================== ON READY ====================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    embed = discord.Embed(
        title=MAIN_MESSAGE_TITLE,
        description=MAIN_MESSAGE_DESCRIPTION
    )

    ch1 = bot.get_channel(APPLICATION_CHANNEL_ID)
    if ch1:
        await ch1.send(embed=embed, view=ApplicationView())

    ch2 = bot.fetch_channel(SECOND_APPLICATION_CHANNEL_ID)
    if ch2:
        await ch2.send(embed=embed, view=ApplicationView())


# ==================== RUN ====================

TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    bot.run(TOKEN)
