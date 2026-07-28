from bot import CustomBot
from discord import Interaction, app_commands
from discord.ext import commands


class Reload(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    async def mode_autocomplete(
        self, _interaction: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        manager = self.bot.state.manager

        choices: list[app_commands.Choice] = []

        for mode in manager.modes:
            name = f"{mode.name} ({mode.mode})"

            if current in name:
                choices.append(app_commands.Choice(name=name, value=mode.name))

        return choices

    @app_commands.command(
        description="Manually refresh data for one or all radio modes"
    )
    @app_commands.autocomplete(mode=mode_autocomplete)
    @app_commands.guild_only()
    async def reload(self, interaction: Interaction, mode: str | None):
        manager = self.bot.state.manager

        if mode and mode not in (m.name for m in manager.modes):
            await interaction.response.send_message(
                f"I couldn't find a mode with the name '{mode}'."
            )
            return

        await interaction.response.defer()

        if await manager.reload([mode] if mode else None):
            await interaction.followup.send(
                f"Refreshed {f"mode '{mode}'" if mode else 'all modes'}."
            )
        else:
            await interaction.followup.send(
                "I'm already in the process of refreshing data."
            )


async def setup(bot: CustomBot):
    await bot.add_cog(Reload(bot))
