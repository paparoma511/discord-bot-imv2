import os
import asyncio
import discord
from discord.ext import commands

# ==================== НАСТРОЙКА БОТА ====================

APPLICATION_CHANNEL_ID = 1463831540386627635  # ID канала, где будет кнопка "Подать заявку"
CATEGORY_ID = 1474492852259262464             # ID категории, где будут создаваться тикеты

# СПИСОК РОЛЕЙ АДМИНИСТРАЦИИ (Вы можете добавить сюда через запятую сколько угодно ID ролей)
ADMIN_ROLE_IDS = [1474489466952351987, 1501898065248915506, 1501898065248915506] 

MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера NORULES"
MAIN_MESSAGE_DESCRIPTION = "Условия при которых ваша заявка будет принята\n-вам должно быть не меньше 13 лет\n-вы должны знать правила сервера\n-вы должны знать регламент администрации сервера\n-у вас должно быть наигранно не менее 50 часов в SCP:SL\n-----------------------------\n⚠️Шуточные заявки будут отклоняться ,а кто подавал шуточную заявку может получить наказание на усмотрение администрации ⚠️"
FORM_TITLE = "Подать заявку"

# ========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Функция для проверки, есть ли у пользователя хотя бы одна админ-роль
def has_admin_role(user: discord.Member) -> bool:
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in ADMIN_ROLE_IDS for role_id in user_role_ids)

# Модальное окно (Форма) для указания причины (Принятия/Отклонения)
class ReasonModal(discord.ui.Modal):
    def __init__(self, action_type: str, candidate: discord.Member):
        title_text = "Причина принятия" if action_type == "approve" else "Причина отклонения"
        super().__init__(title=title_text)
        self.action_type = action_type
        self.candidate = candidate

        self.reason = discord.ui.TextInput(
            label="Введите причину/комментарий для кандидата:",
            placeholder="Ваши навыки подходят... / Вы не подходите по возрасту...",
            style=discord.TextStyle.long,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if not has_admin_role(interaction.user):
            await interaction.followup.send("❌ У вас нет прав для выполнения этого действия!", ephemeral=True)
            return

        try:
            if self.action_type == "approve":
                await self.candidate.send(f"🎉 **Ваша заявка ПРИНЯТА!**\n**Комментарий:** {self.reason.value}")
                await interaction.channel.send("📥 Заявка принята. Канал будет удален через 5 секунд...")
            else:
                await self.candidate.send(f"❌ **Ваша заявка ОТКЛОНЕНА.**\n**Причина:** {self.reason.value}")
                await interaction.channel.send("📥 Заявка отклонена. Канал будет удален через 5 секунд...")
            
            await asyncio.sleep(5)
            await interaction.channel.delete()

        except discord.Forbidden:
            await interaction.channel.send(f"⚠️ Ошибка: Либо у кандидата закрыто ЛС, либо у бота нет прав 'Управлять каналами'. Канал не удален.")


# Панель управления заявкой внутри тикета (Для админов)
class AdminTicketView(discord.ui.View):
    def __init__(self, candidate_id: int):
        super().__init__(timeout=None)
        self.candidate_id = candidate_id

    @discord.ui.button(label="Взять на рассмотрение", style=discord.ButtonStyle.blurple, custom_id="admin:review")
    async def review_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        if not has_admin_role(interaction.user):
            await interaction.followup.send("❌ У вас нет прав для управления заявками!", ephemeral=True)
            return

        candidate = interaction.guild.get_member(self.candidate_id)
        if not candidate:
            await interaction.channel.send("❌ Кандидат покинул сервер.")
            return

        try:
            await candidate.send(f"👀 **Ваша заявка взята на рассмотрение администрацией!**")
            await interaction.channel.send(f"⚙️ {interaction.user.mention} взял заявку на рассмотрение. Кандидату отправлено уведомление в ЛС.")
            
            button.disabled = True
            await interaction.message.edit(view=self)
        except discord.Forbidden:
            await interaction.channel.send(f"⚠️ Заявка на рассмотрении, но у {candidate.mention} закрыты ЛС.")

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.success, custom_id="admin:approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidate = interaction.guild.get_member(self.candidate_id)
        if not candidate:
            await interaction.response.send_message("❌ Кандидат покинул сервер.", ephemeral=True)
            return
        await interaction.response.send_modal(ReasonModal(action_type="approve", candidate=candidate))

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger, custom_id="admin:reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidate = interaction.guild.get_member(self.candidate_id)
        if not candidate:
            await interaction.response.send_message("❌ Кандидат покинул сервер.", ephemeral=True)
            return
        await interaction.response.send_modal(ReasonModal(action_type="reject", candidate=candidate))


# Основная форма подачи анкеты кандидата
class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)

        self.name = discord.ui.TextInput(label="Ваш игровой никнейм", placeholder="", min_length=2, max_length=30)
        self.steanid = discord.ui.TextInput(label="Ваш SteamID@steam", placeholder="76xxxxx@steam", max_length=50)
        self.linksteam = discord.ui.TextInput(label="Ссылка на ваш Steam Аккаунт", placeholder="ОН ДОЛЖЕН БЫТЬ НЕ ПРИВАТНЫМ", max_length=100)
        self.experience = discord.ui.TextInput(label="Был ли опыт работы администратором?", placeholder="Да/нет", max_length=3)
        self.about = discord.ui.TextInput(label="Расскажите немного о себе", placeholder="Почему именно вы должны занять эту должность?", style=discord.TextStyle.long)

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
            await interaction.followup.send("❌ Ошибка: Категория для заявок настроена неверно!", ephemeral=True)
            return

        # Настраиваем права: скрываем от всех, открываем для кандидата и бота
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)
        }

        # Открываем права для каждой админ-роли из нашего списка настроек
        for role_id in ADMIN_ROLE_IDS:
            admin_role = guild.get_role(role_id)
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)

        channel_name = f"заявка-{member.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        embed = discord.Embed(title="📥 Новая заявка на должность!", color=discord.Color.green())
        embed.add_field(name="Кандидат:", value=f"{member.mention} ({member.name})", inline=False)
        embed.add_field(name="Как вас зовут и сколько вам лет?", value=self.name.value, inline=False)
        embed.add_field(name="Ваш часовой пояс и онлайн в день?", value=self.timezone.value, inline=False)
        embed.add_field(name="Был ли опыт работы модератором?", value=self.experience.value or "Не указано", inline=False)
        embed.add_field(name="Расскажите немного о себе", value=self.about.value, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ticket_channel.send(
            content="🔔 Получена новая анкета!", 
            embed=embed, 
            view=AdminTicketView(candidate_id=member.id)
        )

        await interaction.followup.send(f"✅ Ваша анкета принята! Создан приватный чат: {ticket_channel.mention}, прочтите правила в категории <#1492091496147451945>", ephemeral=True)


# Класс вечной стартовой кнопки
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.success, custom_id="persistent_view:apply_ticket")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())


@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))
    bot.add_view(ApplicationView())


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_apps(ctx):
    channel = bot.get_channel(APPLICATION_CHANNEL_ID)
    if channel is None:
        await ctx.send("❌ Ошибка: Не удалось найти канал. Проверьте ID в main.py!")
        return

    embed = discord.Embed(title=MAIN_MESSAGE_TITLE, description=MAIN_MESSAGE_DESCRIPTION, color=discord.Color.blue())
    await channel.send(embed=embed, view=ApplicationView())
    await ctx.send(f"✅ Кнопка заявок отправлена в канал {channel.mention}!")


TOKEN = os.environ.get("BOT_TOKEN")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        raise RuntimeError("BOT_TOKEN не установлен в переменных окружения!")
