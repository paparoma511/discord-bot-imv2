import os
import discord
from discord.ext import commands
from dotenv import load_dotenv  # Исправлено здесь!

# Автоматически загружаем переменные из .env файла, если он есть
load_dotenv()

# Настройка намерений (Intents)
intents = discord.Intents.default()
intents.message_content = True  # Разрешает читать текст сообщений
intents.members = True          # Разрешает видеть список участников

# Создание экземпляра бота и выбор префикса для команд (!)
bot = commands.Bot(command_prefix="!", intents=intents)

# Событие: Бот успешно подключился к Discord
@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    # Установка статуса "Играет в ..."
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))

# Простая команда тестирования (!ping)
@bot.command()
async def ping(ctx):
    """Проверяет задержку бота"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

# Команда для приветствия пользователя (!hello)
@bot.command()
async def hello(ctx):
    """Приветствует автора сообщения"""
    await ctx.send(f"Привет, {ctx.author.mention}! Рад тебя видеть. 👋")

# Считываем токен из настроек вашего хостинга (из переменной BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    bot.run(TOKEN)




