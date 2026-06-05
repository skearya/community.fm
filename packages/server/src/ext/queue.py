import hashlib
import json
from dataclasses import asdict

import discord
from bot import CustomBot
from discord import Interaction, app_commands
from discord.ext import commands
from pls import Album, Media, MediaType, Playlist, Summary, Track


class Queue(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.autocomplete_to_summary: dict[str, Summary] = {}

    @app_commands.command(
        name="queue-url", description="Queue a song onto the radio from a URL."
    )
    @app_commands.describe(url="YouTube/Qobuz/Tidal/Deezer/Soundcloud supported")
    @app_commands.guild_only()
    async def queue_url(self, interaction: Interaction, url: str):
        await interaction.response.defer()

        pls = self.bot.state.pls

        media = await pls.url(url)

        if media is None:
            await interaction.followup.send(
                "I failed to fetch needed metadata from this URL. Are you using a supported service (YouTube/Qobuz/Tidal/Deezer/Soundcloud)?",
                ephemeral=True,
            )
            return

        embed = await self.queue_process_media(interaction.user.name, media)
        await interaction.followup.send(embed=embed)

    async def query_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        pls = self.bot.state.pls

        type = interaction.namespace.type
        service = interaction.namespace.service

        if not type or not current:
            return []

        results = await pls.search(
            query=current,
            type=interaction.namespace.type,
            services=[service] if service else None,
        )

        choices: list[app_commands.Choice] = []

        for summary in results[:25]:
            string = json.dumps(asdict(summary), sort_keys=True)
            hash = hashlib.md5(string.encode("utf-8")).hexdigest()

            self.autocomplete_to_summary[hash] = summary

            name = f"{summary.id[0]} | {summary.artist} - {summary.title}"
            value = hash

            choices.append(app_commands.Choice(name=name[:100], value=value))

        return choices

    async def service_autocomplete(
        self, _interaction: discord.Interaction, _current: str
    ) -> list[app_commands.Choice[str]]:
        pls = self.bot.state.pls

        return [
            app_commands.Choice(name=service, value=service)
            for service in pls.services()
        ]

    @app_commands.command(
        name="queue-search",
        description="Queue a song onto the radio through searching.",
    )
    @app_commands.describe(
        type="track or album or playlist", query="'artist' - 'title' recommended"
    )
    @app_commands.autocomplete(query=query_autocomplete, service=service_autocomplete)
    @app_commands.guild_only()
    async def queue_search(
        self,
        interaction: Interaction,
        type: MediaType,
        query: str,
        service: str | None = None,
    ):
        await interaction.response.defer()

        pls = self.bot.state.pls

        summary = self.autocomplete_to_summary.get(query) or await pls.best(
            query, type, [service] if service else None
        )

        if summary is None:
            await interaction.followup.send(
                "I failed to find a close enough match, try selecting an autocomplete option or queuing a URL."
            )
            return

        media = await pls.info(*summary.id, summary.type)

        if media is None:
            await interaction.followup.send(
                f"I failed to fetch needed metadata for {summary.title} by {summary.artist} ({summary.id[0]}), please try another service."
            )
            return

        embed = await self.queue_process_media(interaction.user.name, media)
        await interaction.followup.send(embed=embed)

    async def queue_process_media(self, username: str, media: Media) -> discord.Embed:
        manager = self.bot.state.manager

        embed = discord.Embed()

        if isinstance(media, Track):
            assert media.id

            embed.title = "Track queued"
            embed.description = f"### {media.title} by {media.artist}"
            embed.set_footer(text=f"{media.id[0]}: {media.id[1]}")

            if media.url:
                embed.url = media.url

            manager.queue.items.append((username, media))
        if isinstance(media, Album | Playlist):
            embed.title = "Album queued"
            embed.description = (
                f"### {media.title} by {media.artist}\n"
                if isinstance(media, Album)
                else f"### {media.title}\n"
            ) + (
                "\n".join(
                    [
                        f"-# {track.title or 'Unknown'} by {track.artist or 'Unknown'}"
                        for track in media.items
                    ]
                )
            )

            embed.set_footer(
                text=", ".join(set([track.id[0] for track in media.items if track.id]))
            )

            if isinstance(media, Album) and media.cover:
                embed.set_thumbnail(url=media.cover)

            manager.queue.items.extend([(username, track) for track in media.items])

        if manager.mode is not manager.queue:
            await manager.switch(manager.queue.name)

        return embed

    @app_commands.command(description="See the current tracks in queue.")
    @app_commands.guild_only()
    async def queue(self, interaction: Interaction):
        manager = self.bot.state.manager

        lines: list[str] = []

        for username, track in manager.queue.items:
            details = " • ".join(
                filter(
                    None,
                    [track.id and f"*{track.id[0]}*", f"*{username}*"],
                )
            )

            lines.append(
                f"**{track.title or 'Unknown'}** by {track.artist or 'Unknown'}\n"
                f"-# {details}",
            )

        embed = discord.Embed(title="Queue", description="\n".join(lines) or "...")

        await interaction.response.send_message(embed=embed)


async def setup(bot: CustomBot):
    await bot.add_cog(Queue(bot))
