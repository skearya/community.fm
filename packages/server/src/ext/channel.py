import csv
import plistlib
from io import StringIO

from bot import CustomBot
from discord import Attachment, Message, utils
from discord.ext import commands
from loguru import logger
from models import ChannelModeEntry
from modes.channel import ChannelMode
from pls import Track


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
                    if message.author.id not in mode.entries and (
                        attachment := self.find(message)
                    ):
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

        if not mode or message.author.bot or not (attachment := self.find(message)):
            return

        if count := await self.update(message, attachment, mode.entries):
            await message.reply(f"Updated {count} channel tracks.")

            logger.info(
                f"Updated {count} '{mode.name}' channel song(s) for '{message.author.name}'"
            )
        else:
            await message.reply(
                "Invalid attachment. Please use [Exportify](https://exportify.app/) or [Export Youtube Playlist](https://export-youtube-playlist.vercel.app/) or [Apple Music's Exporter](https://support.apple.com/guide/music/save-a-copy-of-your-playlists-mus27cd5060f/mac)"
            )

    def find(self, message: Message) -> Attachment | None:
        return next(
            (
                a
                for a in message.attachments
                if a.content_type
                and a.content_type.startswith(("text/csv", "application/xml"))
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
            assert attachment.content_type

            async with self.bot.state.session.get(attachment.url) as response:
                response.raise_for_status()
                text = await response.text()

            if not (
                tracks := (
                    self.csv(text)
                    if attachment.content_type.startswith("text/csv")
                    else self.xml(text)
                    if attachment.content_type.startswith("application/xml")
                    else None
                )
            ):
                return None

            entries[message.author.id] = ChannelModeEntry(
                message.author.display_name, message.author.display_avatar.url, tracks
            )

            return len(tracks)
        except Exception:
            logger.exception("Failed to ingest channel attachment")
            return None

    def csv(self, text: str) -> list[Track] | None:
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

    def xml(self, text: str) -> list[Track] | None:
        data = plistlib.loads(text)

        return [
            Track(
                id=("apple", track["Track ID"]),
                url=None,
                isrc=None,
                title=track["Name"],
                artist=track["Artist"],
            )
            for track in data["Tracks"].values()
        ]


async def setup(bot: CustomBot):
    await bot.add_cog(ChannelIngester(bot))
