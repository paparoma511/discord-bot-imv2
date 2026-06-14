import os
import discord
from discord.ext import commands

# 1. Настройка намерений (Intents)
# Без этого бот запустится, но не будет видеть сообщения и участников
intents = discord.Intents.default()
intents.message_content = True  # Разрешает читать текст сообщений
intents.members = True          # Разрешает видеть список участников

# 2. Создание экземпляра бота и выбор префикса для команд (например, !)
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. Событие: Бот успешно подключился к Discord
@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    # Установка статуса "Играет в ..."
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))

# 4. Простая команда тестирования (!ping)
@bot.command()
async def ping(ctx):
    """Проверяет задержку бота"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

# 5. Команда для приветствия пользователя (!hello)
@bot.command()
async def hello(ctx):
    """Приветствует автора сообщения"""
    await ctx.send(f"Привет, {ctx.author.mention}! Рад тебя видеть. 👋")

# 6. Запуск бота с помощью токена
# Замените 'ВАШ_ТОКЕН_БОТА' на настоящий токен из Developer Portal
# Важно: Не удаляйте кавычки вокруг токена!
TOKEN = "MTUxMDM5MTQwNjUyMTIyNTM3OA.GtV0LX.ncZAgKIco17ceq0YNHPKdmuDYvgl8bWuV_TVWc"

if __name__ == "__main__":
    bot.run(TOKEN)
