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

class ReasonModal(discord.ui.Modal):
    def __init__(self, action_type: str, candidate: discord.Member):
        super().__init__(title="Причина принятия" if action_type == "approve" else "Причина отклонения")
        self.action_type = action_type
        self.candidate = candidate
        self.reason = discord.ui.TextInput(label="Укажите причину решения", style=discord.TextStyle.long, max_length=500, required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        status = "ПРИНЯТА" if self.action_type == "approve" else "ОТКЛОНЕНА"
        color = discord.Color.green() if self.action_type == "approve" else discord.Color.red()
        try:
            embed = discord.Embed(title="Результат рассмотрения", description=f"Ваша заявка была **{status}**.\n\n**Причина:** {self.reason.value}", color=color)
            await self.candidate.send(embed=embed)
        except Exception: pass
        await interaction.followup.send(f"Тикет обработан. Удаление...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketControlView(discord.ui.View):
    def __init__(self, candidate: discord.Member):
        super().__init__(timeout=None)
        self.candidate = candidate

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.green, custom_id="btn_approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_admin_role(interaction.user): return await interaction.response.send_message("Нет прав.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal("approve", self.candidate))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.red, custom_id="btn_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_admin_role(interaction.user): return await interaction.response.send_message("Нет прав.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal("deny", self.candidate))

class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)
        self.age = discord.ui.TextInput(label="Ваш возраст", placeholder="15", min_length=2, max_length=2)
        self.hours = discord.ui.TextInput(label="Сколько часов в SCP:SL?", placeholder="120")
        self.experience = discord.ui.TextInput(label="Имеется ли опыт?", style=discord.TextStyle.long, required=False)
        self.about = discord.ui.TextInput(label="Расскажите о себе", style=discord.TextStyle.long)
        self.add_item(self.age); self.add_item(self.hours); self.add_item(self.experience); self.add_item(self.about)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        category = interaction.guild.get_channel(CATEGORY_ID)
        if not category: return await interaction.followup.send("Категория не найдена.", ephemeral=True)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        for r_id in ADMIN_ROLE_IDS:
            r = interaction.guild.get_role(r_id)
            if r: overwrites[r] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(name=f"заявка-{interaction.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(title=f"Анкета от {interaction.user.display_name}", color=discord.Color.blue())
        embed.add_field(name="Возраст", value=self.age.value); embed.add_field(name="Часы", value=self.hours.value)
        embed.add_field(name="Опыт", value=self.experience.value or "Нет", inline=False); embed.add_field(name="О себе", value=self.about.value, inline=False)
        await ch.send(embed=embed, view=TicketControlView(interaction.user))
        await interaction.followup.send(f"Тикет создан: {ch.mention}", ephemeral=True)

class ComplaintControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.red, custom_id="btn_close_complaint")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_mod_role(interaction.user): return await interaction.response.send_message("Нет прав.", ephemeral=True)
        await interaction.response.send_message("Удаление через 3 секунды...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class ComplaintModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=COMPLAINT_FORM_TITLE)
        self.offender = discord.ui.TextInput(label="Никнейм нарушителя")
        self.rule = discord.ui.TextInput(label="Какое правило нарушено?")
        self.evidence = discord.ui.TextInput(label="Доказательства (Ссылки)", style=discord.TextStyle.long)
        self.details = discord.ui.TextInput(label="Описание", style=discord.TextStyle.long, required=False)
        self.add_item(self.offender); self.add_item(self.rule); self.add_item(self.evidence); self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        category = interaction.guild.get_channel(COMPLAINT_CATEGORY_ID)
        if not category: return await interaction.followup.send("Категория не найдена.", ephemeral=True)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        for r_id in MOD_ROLE_IDS:
            r = interaction.guild.get_role(r_id)
            if r: overwrites[r] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(name=f"жалоба-{interaction.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(title=f"Жалоба от {interaction.user.display_name}", color=discord.Color.red())
        embed.add_field(name="Нарушитель", value=self.offender.value); embed.add_field(name="Правило", value=self.rule.value)
        embed.add_field(name="Доказательства", value=self.evidence.value, inline=False); embed.add_field(name="Суть", value=self.details.value or "Нет", inline=False)
        pings = " ".join([f"<@&{r_id}>" for r_id in MOD_ROLE_IDS if interaction.guild.get_role(r_id)])
        await ch.send(content=pings, embed=embed, view=ComplaintControlView())
        await interaction.followup.send(f"Жалоба отправлена: {ch.mention}", ephemeral=True)

class StartAppView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.blurple, custom_id="start_application")
    async def start_app(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_modal(ApplicationModal())

class StartComplaintView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Подать жалобу", style=discord.ButtonStyle.danger, custom_id="start_complaint")
    async def start_comp(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_modal(ComplaintModal())

@bot.event
async def on_ready():
    bot.add_view(StartAppView()); bot.add_view(StartComplaintView()); bot.add_view(ComplaintControlView())
