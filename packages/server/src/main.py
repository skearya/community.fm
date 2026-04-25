from os import environ

import discord
from bot import CustomBot

BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]

if __name__ == "__main__":
    if "OPUS_LIB_PATH" in environ:
        discord.opus.load_opus(environ["OPUS_LIB_PATH"])

    CustomBot().run(BOT_TOKEN)
