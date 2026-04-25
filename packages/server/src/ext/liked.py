import csv
from io import StringIO
from typing import Optional
from loguru import logger

from bot import CustomBot
from discord import Message, utils, Attachment
from discord.ext import commands

LIKED_SONGS_CHANNEL = "liked-songs"
CSV_ATTRIBUTES = ["Track Name", "Artist Name(s)", "ISRC"]
CSV_CONTENT_TYPE = "text/csv"


class LikedSongs(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.songs: dict[int, list[dict]] = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Get each user's most recently uploaded songs."""
        logger.info("Getting liked songs...")
        for guild in self.bot.guilds:
            channel = utils.get(guild.text_channels, name=LIKED_SONGS_CHANNEL)
            if channel is None:
                continue

            async for message in channel.history(oldest_first=False):
                if message.author.id in self.songs:
                    continue
                songs = await self._extract_songs(message)
                if songs is None:
                    continue
                self.songs[message.author.id] = songs
        logger.info(f"Got liked songs for {len(self.songs)} user(s).")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Update a user's liked songs upon sending a CSV."""
        author = message.author
        if author.bot or str(message.channel) != LIKED_SONGS_CHANNEL:
            return

        if self._find_csv(message) is None:
            return

        songs = await self._extract_songs(message)
        if songs is None:
            await message.reply("Invalid CSV. Please use https://exportify.app/")
            return

        self.songs[author.id] = songs
        await message.reply(f"Updated {len(songs)} liked songs.")
        logger.info(f"Updated {len(songs)} liked song(s) for: {author.name}")

    async def _extract_songs(self, message: Message) -> Optional[list[dict[str, str]]]:
        """Find, fetch, and parse a CSV from a message."""
        attachment = self._find_csv(message)
        if attachment is None:
            return None
        csv_text = await self._fetch_csv(attachment)
        return self._parse_csv(csv_text)

    def _find_csv(self, message: Message) -> Optional[Attachment]:
        return next(
            (
                a
                for a in message.attachments
                if a.content_type and a.content_type.startswith(CSV_CONTENT_TYPE)
            ),
            None,
        )

    async def _fetch_csv(self, attachment: Attachment) -> str:
        async with self.bot.session.get(attachment.url) as response:
            response.raise_for_status()
            return await response.text()

    def _parse_csv(self, csv_text: str) -> Optional[list[dict[str, str]]]:
        reader = csv.DictReader(StringIO(csv_text))
        if reader.fieldnames is None or not all(
            attr in reader.fieldnames for attr in CSV_ATTRIBUTES
        ):
            return None
        return [{col: row[col] for col in CSV_ATTRIBUTES} for row in reader]


async def setup(bot: CustomBot):
    await bot.add_cog(LikedSongs(bot))
