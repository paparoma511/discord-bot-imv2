import os
import discord
from discord.ext import commands

# ==================== НАСТРОЙКА БОТА ====================

# 1. ID канала, куда бот отправит сообщение с кнопкой
APPLICATION_CHANNEL_ID = 1463831540386627635  # Замените на реальный ID канала

# 2. ID КАТЕГОРИИ, где бот будет создавать личные чаты для заявок
CATEGORY_ID = 1474492852259262464  # Замените на реальный ID категории!

# 3. Текст сообщения, который увидят пользователи на сервере
MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера (ТЕСТ РЕЖИМ)"
MAIN_MESSAGE_DESCRIPTION = "Нажмите на кнопку ниже, чтобы заполнить анкету. Для вас автоматически создастся отдельный чат-заявка."

# 4. Настройка самой формы (Модального окна)
FORM_TITLE = "Ваша анкета"  # Заголовок всплывающего окна

# ========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Класс всплывающего окна (Формы)
class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)

        # Поля анкеты (максимум 5 штук)
        self.name = discord.ui.TextInput(
            label="Ваш игровой никнейм",
            placeholder="",
            min_length=2,
            max_length=50,
            style=discord.TextStyle.short
        )
        self.timezone = discord.ui.TextInput(
            label="Сколько вам лет?",
            placeholder="",
            max_length=30,
            style=discord.TextStyle.short
        )
        self.experience = discord.ui.TextInput(
            label="Был ли опыт работы администратором?",
            placeholder="Да/Нет",
            max_length=30,
            style=discord.TextStyle.short
        )
        self.about = discord.ui.TextInput(
            label="Расскажите немного о себе",
            placeholder="",
            style=discord.TextStyle.long
        )
        self.admin = discord.ui.TextInput(
            label="Почему вы должны стать администратором?",
            placeholder="",
            style=discord.TextStyle.long
        )

        self.add_item(self.name)
        self.add_item(self.timezone)
        self.add_item(self.experience)
        self.add_item(self.about)
        self.add_item(self.admin)

    # Логика отправки анкеты и создания чата
    async def on_submit(self, interaction: discord.Interaction):
        # Говорим Discord, что мы начали обрабатывать запрос (чтобы не было ошибки таймаута)
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user

        # Ищем категорию, в которой создавать канал
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        if not category:
            await interaction.followup.send("❌ Ошибка: Администрация не настроила категорию для заявок!", ephemeral=True)
            return

        # Настраиваем права доступа для нового канала:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Всем остальным читать запрещено
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True), # Кандидату разрешено
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True) # Боту разрешено
        }

        # Создаем приватный канал внутри выбранной категории
        channel_name = f"заявка-{member.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        # Оформляем анкету в красивый Embed
        embed = discord.Embed(title="📥 Новая заявка на должность!", color=discord.Color.green())
        embed.add_field(name="Кандидат:", value=f"{member.mention} ({member.name})", inline=False)
        embed.add_field(name=self.name.label, value=self.name.value, inline=False)
        embed.add_field(name=self.timezone.label, value=self.timezone.value, inline=False)
        embed.add_field(name=self.experience.label, value=self.experience.value or "Не указано", inline=False)
        embed.add_field(name=self.about.label, value=self.about.value, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        # Отправляем анкету в только что созданный приватный чат и тегаем кандидата/админов
        await ticket_channel.send(content=f"{member.mention} | Администрация скоро свяжется с вами в этом канале!", embed=embed)

        # Уведомляем пользователя лично, что чат успешно создан
        await interaction.followup.send(f"✅ Ваша анкета принята! Для вас создан приватный чат: {ticket_channel.mention}", ephemeral=True)


# Класс постоянной кнопки
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Кнопка не отключится после перезапуска

    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.success, custom_id="persistent_view:apply_ticket")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())


@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))
    
    # Регистрируем кнопку в памяти бота
    bot.add_view(ApplicationView())


# Команда для отправки сообщения с кнопкой (вызывает админ)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_apps(ctx):
    channel = bot.get_channel(APPLICATION_CHANNEL_ID)
    if channel is None:
        await ctx.send("❌ Ошибка: Не удалось найти канал для кнопки. Проверьте ID в main.py!")
        return

    embed = discord.Embed(
        title=MAIN_MESSAGE_TITLE,
        description=MAIN_MESSAGE_DESCRIPTION,
        color=discord.Color.blue()
    )
    
    await channel.send(embed=embed, view=ApplicationView())
    await ctx.send(f"✅ Кнопка заявок отправлена в канал {channel.mention}!")


TOKEN = os.environ.get("BOT_TOKEN")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ОШИБКА: Переменная BOT_TOKEN пуста или не найдена на Bothost!")
    else:
        bot.run(TOKEN)
