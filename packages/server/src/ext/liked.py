from typing import Optional
from discord import Interaction, app_commands, Message
from discord.ext import commands
from main import CustomBot
from io import StringIO
import requests
import csv

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

        response = requests.get(attachment.url)
        response.raise_for_status()

        songs = self._parse_songs(response.text)
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
