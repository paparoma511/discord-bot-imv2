import os

import discord

from discord.ext import commands

from dotenv import load_dotenv

from database.database import create_database


from views.application_buttons import ApplicationView

from views.close_buttons import CloseView

from views.admin_buttons import AdminView



load_dotenv()



TOKEN = os.getenv(
    "BOT_TOKEN"
)



intents = discord.Intents.default()

intents.message_content = True

intents.members = True



bot = commands.Bot(

    command_prefix="!",

    intents=intents

)



@bot.event
async def on_ready():


    print(
        f"ONLINE: {bot.user}"
    )


    bot.add_view(
        ApplicationView()
    )


    bot.add_view(
        CloseView(0)
    )


    bot.add_view(
        AdminView(0)
    )


    await bot.tree.sync()



# загрузка модулей

async def load_extensions():


    await bot.load_extension(
        "cogs.applications"
    )


    await bot.load_extension(
        "cogs.reports"
    )


    await bot.load_extension(
        "cogs.moderation"
    )



async def main():


    async with bot:


        await create_database()


        await load_extensions()



import asyncio

asyncio.run(main())