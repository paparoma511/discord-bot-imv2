print("FILE STARTED")

import os

import discord

from discord.ext import commands

from dotenv import load_dotenv


from views.application_buttons import ApplicationView
from views.close_buttons import CloseView
from views.admin_buttons import AdminView

from database.database import create_database



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


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    print(
        f"COMMAND ERROR: {error}"
    )

    try:

        await interaction.response.send_message(
            f"❌ Ошибка:\n```{error}```",
            ephemeral=True
        )

    except:

        pass


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

    print("Loading cogs")


    await bot.load_extension(
        "cogs.applications"
    )

    print("Applications loaded")


    await bot.load_extension(
        "cogs.reports"
    )

    print("Reports loaded")


    await bot.load_extension(
        "cogs.moderation"
    )

    print("Moderation loaded")


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