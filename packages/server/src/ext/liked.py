import csv
from io import StringIO

from bot import CustomBot
from discord import Attachment, Message, utils
from discord.ext import commands
from loguru import logger
from models import LikedSongEntry
from pls import Request

LIKED_SONGS_CHANNEL = "liked-songs"
CSV_CONTENT_TYPE = "text/csv"


class LikedSongs(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Get each user's most recently uploaded songs."""
        logger.info("Getting liked songs...")
        for guild in self.bot.guilds:
            if channel := utils.get(guild.text_channels, name=LIKED_SONGS_CHANNEL):
                async for message in channel.history(oldest_first=False):
                    author = message.author
                    if author.id in self.bot.state.liked:
                        continue
                    if songs := await self._extract_songs(message):
                        self.update_songs(author.id, author.name, songs)
        logger.info(f"Got liked songs for {len(self.bot.state.liked)} user(s).")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Update a user's liked songs upon sending a CSV."""
        author = message.author
        if author.bot or str(message.channel) != LIKED_SONGS_CHANNEL:
            return

        if self.find_csv(message) is None:
            return  # don't reply to messages without csvs

        if songs := await self._extract_songs(message):
            self.update_songs(author.id, author.name, songs)
            await message.reply(f"Updated {len(songs)} liked songs.")
            logger.info(f"Updated {len(songs)} liked song(s) for: {author.name}")
        else:
            await message.reply(
                "Invalid CSV. Please use https://exportify.app/ or https://export-youtube-playlist.vercel.app/"
            )

    def update_songs(self, user_id: int, username: str, songs: list[Request]) -> None:
        self.bot.state.liked[user_id] = LikedSongEntry(username, songs)

    async def _extract_songs(self, message: Message) -> list[Request] | None:
        """Find, fetch, and parse a CSV from a message."""
        if attachment := self.find_csv(message):
            csv_text = await self._fetch_csv(attachment)
            return self.parse_csv(csv_text)
        else:
            return None

    def find_csv(self, message: Message) -> Attachment | None:
        return next(
            (
                a
                for a in message.attachments
                if a.content_type and a.content_type.startswith(CSV_CONTENT_TYPE)
            ),
            None,
        )

    async def _fetch_csv(self, attachment: Attachment) -> str:
        async with self.bot.state.session.get(attachment.url) as response:
            response.raise_for_status()
            return await response.text()

    def parse_csv(self, csv_text: str) -> list[Request] | None:
        try:
            reader = csv.DictReader(StringIO(csv_text))
            if reader.fieldnames is None:
                return None

            if all(
                attr in reader.fieldnames
                for attr in ["Track Name", "Artist Name(s)", "ISRC"]
            ):
                return [
                    Request(
                        url=None,
                        isrc=row["ISRC"],
                        name=row["Track Name"],
                        artist=row["Artist Name(s)"],
                    )
                    for row in reader
                ]

            if all(attr in reader.fieldnames for attr in ["Title", "Video url"]):
                return [
                    Request(url=row["Video url"], isrc=None, name=None, artist=None)
                    for row in reader
                ]

            return None
        except Exception:
            return None


async def setup(bot: CustomBot):
    await bot.add_cog(LikedSongs(bot))
