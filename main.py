print("FILE STARTED")


import os
import asyncio


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


print(
    "TOKEN EXISTS:",
    bool(TOKEN)
)



intents = discord.Intents.default()

intents.members = True

intents.message_content = True



bot = commands.Bot(

    command_prefix="!",

    intents=intents

)



# ================= LOAD COGS =================


async def load_extensions():


    print("LOADING COGS...")


    await bot.load_extension(
        "cogs.applications"
    )

    print(
        "APPLICATIONS LOADED"
    )


    await bot.load_extension(
        "cogs.reports"
    )

    print(
        "REPORTS LOADED"
    )


    await bot.load_extension(
        "cogs.moderation"
    )

    print(
        "MODERATION LOADED"
    )



# ================= READY =================


@bot.event

async def on_ready():


    print(
        "BOT READY"
    )


    print(
        f"ONLINE: {bot.user}"
    )


    # постоянные кнопки

    bot.add_view(
        ApplicationView()
    )


    bot.add_view(
        CloseView(0)
    )


    bot.add_view(
        AdminView(0)
    )


    try:


        synced = await bot.tree.sync()


        print(

            f"SYNCED COMMANDS: {len(synced)}"

        )


    except Exception as e:


        print(
            "SYNC ERROR:",
            e
        )



# ================= ERROR =================


@bot.tree.error

async def command_error(

    interaction: discord.Interaction,

    error

):


    print(
        "COMMAND ERROR:",
        error
    )


    try:


        await interaction.response.send_message(

            f"❌ Ошибка:\n```{error}```",

            ephemeral=True

        )


    except:


        pass



# ================= START =================


async def main():


    print(
        "MAIN START"
    )


    async with bot:


        print(
            "BOT CONTEXT"
        )


        await create_database()


        print(
            "DATABASE OK"
        )


        await load_extensions()


        print(
            "COGS LOADED"
        )


        await bot.start(
            TOKEN
        )



if __name__ == "__main__":


    asyncio.run(
        main()
    )