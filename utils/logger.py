from config import LOG_CHANNEL_ID



async def log(bot, text):

    try:

        channel = await bot.fetch_channel(
            LOG_CHANNEL_ID
        )


        await channel.send(
            f"ℹ️ **LOGGER**\n{text}"
        )


    except Exception:

        pass