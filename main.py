import os
import discord
from discord.ext import commands
from dotenv import load_model_or_variables  # Добавим загрузку .env

# Загружаем переменные из скрытого файла .env
load_model_or_variables() if os.path.exists(".env") else None

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

# Теперь мы берем токен из скрытых переменных хостинга, а не пишем его в код!
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    bot.run(TOKEN)


