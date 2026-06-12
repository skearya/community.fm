import csv
from io import StringIO

from bot import CustomBot
from discord import Attachment, Message, utils
from discord.ext import commands
from loguru import logger
from models import ChannelModeEntry
from modes.channel import ChannelMode
from pls import Track

CSV_CONTENT_TYPE = "text/csv"


class ChannelIngester(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for mode in self.bot.state.manager.modes:
            if not isinstance(mode, ChannelMode):
                continue

            logger.info(f"Getting channel tracks for '{mode.name}'.")

            for guild in self.bot.guilds:
                if not (
                    channel := utils.get(guild.text_channels, name=mode.channel_name)
                ):
                    continue

                async for message in channel.history(oldest_first=False):
                    if message.author.id in mode.entries or not (
                        attachment := self.find_attachment(message)
                    ):
                        continue

                    await self.update(message, attachment, mode.entries)

            logger.info(f"Got channel tracks for {len(mode.entries)} user(s).")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        mode = next(
            (
                mode
                for mode in self.bot.state.manager.modes
                if isinstance(mode, ChannelMode)
                and mode.channel_name == str(message.channel)
            ),
            None,
        )

        if (
            not mode
            or message.author.bot
            or not (attachment := self.find_attachment(message))
        ):
            return

        if count := await self.update(message, attachment, mode.entries):
            await message.reply(f"Updated {count} channel tracks.")

            logger.info(
                f"Updated {count} '{mode.name}' channel song(s) for '{message.author.name}'"
            )
        else:
            await message.reply(
                "Invalid CSV. Please use https://exportify.app/ or https://export-youtube-playlist.vercel.app/"
            )

    def find_attachment(self, message: Message) -> Attachment | None:
        return next(
            (
                a
                for a in message.attachments
                if a.content_type and a.content_type.startswith(CSV_CONTENT_TYPE)
            ),
            None,
        )

    async def update(
        self,
        message: Message,
        attachment: Attachment,
        entries: dict[int, ChannelModeEntry],
    ) -> int | None:
        try:
            async with self.bot.state.session.get(attachment.url) as response:
                response.raise_for_status()
                text = await response.text()

            if not (tracks := self.parse(text)):
                return None

            entries[message.author.id] = ChannelModeEntry(message.author.name, tracks)
            return len(tracks)
        except Exception:
            logger.exception("Failed to ingest channel CSV")
            return None

    def parse(self, text: str) -> list[Track] | None:
        reader = csv.DictReader(StringIO(text))

        if reader.fieldnames is None:
            return None

        if all(
            attr in reader.fieldnames
            for attr in ["Track Name", "Artist Name(s)", "ISRC"]
        ):
            return [
                Track(
                    id=None,
                    url=None,
                    isrc=row["ISRC"],
                    title=row["Track Name"],
                    artist=row["Artist Name(s)"],
                )
                for row in reader
            ]

        if all(
            attr in reader.fieldnames for attr in ["Title", "Video url", "Channel name"]
        ):
            return [
                Track(
                    id=None,
                    url=row["Video url"],
                    isrc=None,
                    title=row["Title"],
                    artist=row["Channel name"],
                )
                for row in reader
            ]

        return None


async def setup(bot: CustomBot):
    await bot.add_cog(ChannelIngester(bot))
