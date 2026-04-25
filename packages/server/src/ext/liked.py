import csv
import aiohttp
from io import StringIO
from typing import Optional

import requests
from bot import CustomBot
from discord import Interaction, Message, app_commands
from discord.ext import commands

# TODO: read channel on startup, get csvs from newest members

LIKED_SONGS_CHANNEL = "liked-songs"
CSV_ATTRIBUTES = ["Track Name", "Artist Name(s)", "ISRC"]
CSV_CONTENT_TYPE = "text/csv"


class LikedSongs(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.songs: dict[int, list[dict]] = {}

    @app_commands.command(description="?")
    @app_commands.guild_only()
    async def cmd(self, interaction: Interaction):
        pass

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or str(message.channel) != LIKED_SONGS_CHANNEL:
            return

        attachment = self._find_csv_attachment(message)
        if attachment is None:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as response:
                response.raise_for_status()
                csv_text = await response.text()

        songs = self._parse_songs(csv_text)
        if not songs:
            await message.reply("Invalid CSV.")
            return

        self.songs[message.author.id] = songs
        await message.reply("Updated liked songs.")

    def _find_csv_attachment(self, message: Message):
        return next(
            (
                a
                for a in message.attachments
                if a.content_type and a.content_type.startswith(CSV_CONTENT_TYPE)
            ),
            None,
        )

    def _parse_songs(self, csv_text: str) -> Optional[list[dict]]:
        reader = csv.DictReader(StringIO(csv_text))
        if not reader.fieldnames or not all(
            attr in reader.fieldnames for attr in CSV_ATTRIBUTES
        ):
            return None

        return [
            {col: row[col] for col in CSV_ATTRIBUTES if col in row} for row in reader
        ]


async def setup(bot: CustomBot):
    await bot.add_cog(LikedSongs(bot))
