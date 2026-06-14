import os
import logging
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

# Настройка логирования и принудительное отключение предупреждений о голосовых библиотеках (PyNaCl)
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logging.getLogger('discord.voice').setLevel(logging.ERROR)

# ==================== НАСТРОЙКА БОТА ====================

# --- 1. Подача заявок в администрацию ---
APPLICATION_CHANNEL_ID = 1463831540386627635  # ID текстового канала с кнопкой
CATEGORY_ID = 1474492852259262464             # ID категории для тикетов-заявок
ADMIN_ROLE_IDS = [1513631902966354111, 1501898065248915506, 1474489466952351987, 1474489959095205972] 

MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера NORULES"
MAIN_MESSAGE_DESCRIPTION = """Условия при которых ваша заявка будет принята
 - вам должно быть не меньше 13 лет
- вы должны знать правила сервера
- вы должны знать регламент администрации сервера
- у вас должно быть наигранно не менее 50 часов в SCP:SL
-----------------------------
⚠️Шуточные заявки будут отклоняться, а кто подавал шуточную заявку может получить наказание на усмотрение администрации ⚠️"""
FORM_TITLE = "Ваша анкета"

# --- 2. Жалобы на игроков ---
COMPLAINT_CHANNEL_ID = 1463832239400816695   # ID текстового канала с кнопкой
COMPLAINT_CATEGORY_ID = 1474492852259262464  # ID категории для тикетов-жалоб
MOD_ROLE_IDS = [1513631902966354111, 1501898065248915506, 1474489466952351987, 1474489959095205972]  # ID ролей модераторов через запятую

COMPLAINT_MAIN_TITLE = "Подача жалобы на игрока"
COMPLAINT_MAIN_DESC = "Нажмите на кнопку ниже, чтобы заполнить форму и сообщить о нарушителе. Модерация рассмотрит её в ближайшее время."
COMPLAINT_FORM_TITLE = "Форма жалобы"

# ========================================================

# Включаем message_content интент, так как теперь мы используем текстовую команду !send
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
        
        embed_user = discord.Embed(
            title="Результат рассмотрения заявки",
            description=f"Ваша заявка на сервере NORULES была **{status}**.\n\n**Причина:** {self.reason.value}",
            color=color
        )
        
        try:
            await self.candidate.send(embed=embed_user)
        except Exception:
            logging.warning("Не удалось отправить ЛС кандидату")

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
            return await interaction.response.send_message("У вас нет прав администратора.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal(action_type="approve", candidate=self.candidate))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.red, custom_id="btn_deny")
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_admin_role(interaction.user):
            return await interaction.response.send_message("У вас нет прав администратора.", ephemeral=True)
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
            return await interaction.followup.send("Ошибка: Категория для тикетов не найдена.", ephemeral=True)

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
            return await interaction.response.send_message("У вас нет прав модератора для закрытия этой жалобы.", ephemeral=True)
        
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
