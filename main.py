import os
import discord
from discord.ext import commands

# 1. Настройка намерений (Intents)
intents = discord.Intents.default()
intents.message_content = True  # Разрешает читать текст сообщений
intents.members = True          # Разрешает видеть список участников

# 2. Создание экземпляра бота и выбор префикса
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. Событие: Бот успешно подключился к Discord
@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))

# 4. Простая команда тестирования (!ping)
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

# 5. Команда для приветствия пользователя (!hello)
@bot.command()
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}! Рад тебя видеть. 👋")

# 6. Безопасное чтение токена из панели хостинга
# Код ищет переменную среды BOT_TOKEN, которую мы укажем в панели хостинга
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ОШИБКА: Переменная BOT_TOKEN не найдена в настройках хостинга!")
    else:
        bot.run(TOKEN)






