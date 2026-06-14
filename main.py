import os
import asyncio
import discord
from discord.ext import commands

# ==================== НАСТРОЙКА БОТА ====================

# --- 1. Подача заявок в администрацию ---
APPLICATION_CHANNEL_ID = 1463831540386627635  # ID канала с кнопкой "Подать заявку"
CATEGORY_ID = 1474492852259262464             # ID категории для тикетов-заявок
ADMIN_ROLE_IDS = [1513631902966354111, 1501898065248915506, 1474489466952351987, 1474489959095205972] 

MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера NORULES"
MAIN_MESSAGE_DESCRIPTION = (
    "Условия при которых ваша заявка будет принята\n"
    " - вам должно быть не меньше 13 лет\n"
    "- вы должны знать правила сервера\n"
    "- вы должны знать регламент администрации сервера\n"
    "- у вас должно быть наигранно не менее 50 часов в SCP:SL\n"
    "-----------------------------\n"
    "⚠️Шуточные заявки будут отклоняться, а кто подавал шуточную заявку "
    "может получить наказание на усмотрение администрации ⚠️"
)
FORM_TITLE = "Ваша анкета"

# --- 2. Жалобы на игроков (НОВОЕ) ---
COMPLAINT_CHANNEL_ID = 1463832239400816695   # ЗАМЕНИТЕ! ID канала с кнопкой "Подать жалобу"
COMPLAINT_CATEGORY_ID = 1474492852259262464  # ЗАМЕНИТЕ! ID категории для тикетов-жалоб
MOD_ROLE_IDS = [1474489466952351987, 1474489959095205972, 1474490447203139736, 1513631902966354111, 1501898065248915506] # ЗАМЕНИТЕ! Роли, которые видят жалобы и кого пингует

COMPLAINT_MAIN_TITLE = "Подача жалобы на игрока"
COMPLAINT_MAIN_DESC = "Нажмите на кнопку ниже, чтобы заполнить форму и сообщить о нарушителе. Модерация рассмотрит её в ближайшее время."
COMPLAINT_FORM_TITLE = "Форма жалобы"

# ========================================================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Вспомогательные проверки ролей
def has_admin_role(user: discord.Member) -> bool:
    return any(role.id in ADMIN_ROLE_IDS for role in user.roles)

def has_mod_role(user: discord.Member) -> bool:
    return any(role.id in MOD_ROLE_IDS for role in user.roles)


# ==================== МОДУЛЬ ЗАЯВОК ====================

class ReasonModal(discord.ui.Modal):
    def __init__(self, action_type: str, candidate: discord.Member):
        title_text = "Причина принятия" if action_type == "approve" else "Причина отклонения"
        super().__init__(title=title_text)
        self.action_type = action_type
        self.candidate = candidate

        self.reason = discord.ui.TextInput(
            label="Укажите причину решения",
            placeholder="Текст причины...",
            style=discord.TextStyle.long,
            max_length=500,
            required=True
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        status = "ПРИНЯТА" if self.action_type == "approve" else "ОТКЛОНЕНА"
        color = discord.Color.green() if self.action_type == "approve" else discord.Color.red()
        
        try:
            embed_user = discord.Embed(
                title="Результат рассмотрения заявки",
                description=f"Ваша заявка на сервере NORULES была **{status}**.\n\n**Причина:** {self.reason.value}",
                color=color
            )
            await self.candidate.send(embed=embed_user)
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ Не удалось отправить ЛС {self.candidate.mention}.", ephemeral=True)

        await interaction.followup.send(f"Заявка {status}. Канал удалится через 5 секунд.")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketControlView(discord.ui.View):
    def __init__(self, candidate: discord.Member):
        super().__init__(timeout=None)
        self.candidate = candidate

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.green, custom_id="btn_approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("У вас нет прав.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal(action_type="approve", candidate=self.candidate))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.red, custom_id="btn_deny")
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("У вас нет прав.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal(action_type="deny", candidate=self.candidate))


class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)
        self.age = discord.ui.TextInput(label="Ваш возраст", placeholder="15", min_length=2, max_length=2)
        self.hours = discord.ui.TextInput(label="Сколько часов в SCP:SL?", placeholder="120")
        self.experience = discord.ui.TextInput(label="Имеется ли опыт?", style=discord.TextStyle.long, required=False)
        self.about = discord.ui.TextInput(label="Расскажите о себе", style=discord.TextStyle.long)
        
        self.add_item(self.age)
        self.add_item(self.hours)
        self.add_item(self.experience)
        self.add_item(self.about)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        
        if not category:
            return await interaction.followup.send("Ошибка: Категория не найдена.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }
        for role_id in ADMIN_ROLE_IDS:
            admin_role = guild.get_role(role_id)
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(name=f"заявка-{interaction.user.name}", category=category, overwrites=overwrites)

        embed = discord.Embed(title=f"Анкета от {interaction.user.display_name}", color=discord.Color.blue())
        embed.add_field(name="Возраст", value=self.age.value, inline=True)
        embed.add_field(name="Часы", value=self.hours.value, inline=True)
        embed.add_field(name="Опыт", value=self.experience.value or "Нет", inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)

        await ticket_channel.send(embed=embed, view=TicketControlView(candidate=interaction.user))
        await interaction.followup.send(f"Заявка создана: {ticket_channel.mention}", ephemeral=True)


# ==================== МОДУЛЬ ЖАЛОБ ====================

class ComplaintControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.red, custom_id="btn_close_complaint")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_mod_role(interaction.user):
            return await interaction.response.send_message("У вас нет прав для закрытия этой жалобы.", ephemeral=True)
        
        await interaction.response.send_message("Тикет закрыт. Канал будет удален через 5 секунд.")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class ComplaintModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=COMPLAINT_FORM_TITLE)
        self.offender = discord.ui.TextInput(label="Никнейм / ID нарушителя", placeholder="Ник игрока")
        self.rule = discord.ui.TextInput(label="Какое правило нарушено?", placeholder="Например: 1.1")
        self.evidence = discord.ui.TextInput(label="Доказательства (Ссылки)", style=discord.TextStyle.long, placeholder="Ссылки на видео/скриншоты")
        self.details = discord.ui.TextInput(label="Описание ситуации", style=discord.TextStyle.long, required=False)

        self.add_item(self.offender)
        self.add_item(self.rule)
        self.add_item(self.evidence)
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        category = guild.get_channel(COMPLAINT_CATEGORY_ID)

        if not category:
            return await interaction.followup.send("Ошибка: Категория для жалоб не найдена.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }
        for role_id in MOD_ROLE_IDS:
            mod_role = guild.get_role(role_id)
            if mod_role:
                overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        complaint_channel = await guild.create_text_channel(name=f"жалоба-{interaction.user.name}", category=category, overwrites=overwrites)

        embed = discord.Embed(title=f"Новая жалоба от {interaction.user.display_name}", color=discord.Color.red())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Нарушитель", value=self.offender.value, inline=True)
        embed.add_field(name="Правило", value=self.rule.value, inline=True)
        embed.add_field(name="Доказательства", value=self.evidence.value, inline=False)
        embed.add_field(name="Суть ситуации", value=self.details.value or "Не указано", inline=False)

        ping_mentions = " ".join([f"<@&{role_id}>" for role_id in MOD_ROLE_IDS if guild.get_role(role_id)])

        await complaint_channel.send(content=ping_mentions, embed=embed, view=ComplaintControlView())
