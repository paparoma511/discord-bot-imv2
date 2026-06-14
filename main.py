import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Робот {bot.user.name} успешно запущен и готов к работе!")
    await bot.change_presence(activity=discord.Game(name="Настройка сервера"))

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}! Рад тебя видеть. 👋")

# На хостинге Bothost.ru переменная считывается так:
TOKEN = os.environ.get("BOT_TOKEN")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ОШИБКА: Переменная BOT_TOKEN пуста или не найдена на Bothost!")
    else:
        bot.run(TOKEN)
