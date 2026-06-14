import os
import discord
from discord.ext import commands

# --- НАСТРОЙКА БОТА ---
# 1. Вставьте сюда ID текстового канала, куда бот должен отправить сообщение с кнопкой
APPLICATION_CHANNEL_ID = 1463831540386627635  # Замените на реальный ID канала

# 2. Текст сообщения, который увидят пользователи на сервере
MAIN_MESSAGE_TITLE = "Подача заявки в администрацию сервера (ТЕСТ РЕЖИМ)"
MAIN_MESSAGE_DESCRIPTION = "Нажмите на кнопку ниже, чтобы заполнить анкету и подать заявку на рассмотрение администрации."

# 3. Настройка самой формы (Модального окна)
FORM_TITLE = "Ваша анкета"  # Заголовок всплывающего окна
# ----------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Класс самого всплывающего окна (Формы)
class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=FORM_TITLE)

        # Ниже вы можете редактировать, добавлять или удалять поля анкеты.
        # Максимум 5 полей в одном окне!
        self.name = discord.ui.TextInput(
            label="Ваш игровой никнейм?",
            placeholder="",
            min_length=2,
            max_length=50,
            style=discord.TextStyle.short
        )
        self.timezone = discord.ui.TextInput(
            label="Ваш часовой пояс?",
            placeholder="МСК или +4 по мск(пример)",
            max_length=30,
            style=discord.TextStyle.short
        )
        self.experience = discord.ui.TextInput(
            label="Был ли у вас опыт?",
            placeholder="Да\нет",
            style=discord.TextStyle.long,
            required=False  # Поле не обязательное для заполнения
        )
        self.about = discord.ui.TextInput(
            label="Расскажите немного о себе",
            placeholder="",
            style=discord.TextStyle.long
        )
        self.about = discord.ui.TextInput(
            label="Почему вы должны стать администратором?",
            placeholder="",
            style=discord.TextStyle.long
        )

        # Добавляем элементы в форму
        self.add_item(self.name)
        self.add_item(self.timezone)
        self.add_item(self.experience)
        self.add_item(self.about)

    # Что происходит после того, как пользователь нажал кнопку "Отправить" в форме
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Ваша заявка успешно отправлена на рассмотрение!", ephemeral=True)
        
        # Оформляем красивое Embed-сообщение с результатами для логов
        embed = discord.Embed(title="📥 Новая заявка на сервере!", color=discord.Color.green())
        embed.add_field(name="Автор заявки:", value=f"{interaction.user.mention} ({interaction.user.name})", inline=False)
        embed.add_field(name=self.name.label, value=self.name.value, inline=False)
        embed.add_field(name=self.timezone.label, value=self.timezone.value, inline=False)
        embed.add_field(name=self.experience.label, value=self.experience.value or "Не указано", inline=False)
        embed.add_field(name=self.about.label, value=self.about.value, inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        # Отправляем результаты в тот же канал (или можно настроить отдельный админ-канал)
        await interaction.channel.send(embed=embed)

# Класс кнопки под сообщением
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None делает кнопку вечной, она не перестанет работать

    # Создаем саму кнопку
    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.success, custom_id="persistent_view:apply")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # При нажатии открываем модальное окно (форму)
        await interaction.response.send_modal(ApplicationModal())

@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))
    
    # Регистрация вечной кнопки, чтобы она работала даже после перезапуска бота
    bot.add_view(ApplicationView())

# Команда для создания сообщения с кнопкой подачи заявки
@bot.command()
@commands.has_permissions(administrator=True) # Доступно только администраторам
async def setup_apps(ctx):
    channel = bot.get_channel(APPLICATION_CHANNEL_ID)
    if channel is None:
        await ctx.send("❌ Ошибка: Не удалось найти канал. Проверьте указанный ID в main.py!")
        return

    # Создаем красивое описание
    embed = discord.Embed(
        title=MAIN_MESSAGE_TITLE,
        description=MAIN_MESSAGE_DESCRIPTION,
        color=discord.Color.blue()
    )
    
    # Отправляем embed-сообщение вместе с кнопкой в целевой канал
    await channel.send(embed=embed, view=ApplicationView())
    await ctx.send(f"✅ Сообщение с кнопкой успешно отправлено в канал {channel.mention}!")

TOKEN = os.environ.get("BOT_TOKEN")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ОШИБКА: Переменная BOT_TOKEN пуста или не найдена на Bothost!")
    else:
        bot.run(TOKEN)


