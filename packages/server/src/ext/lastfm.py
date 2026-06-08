from urllib.parse import urlencode

from bot import CustomBot
from discord import ButtonStyle, Interaction, app_commands, ui
from discord.ext import commands
from loguru import logger


class Login(ui.LayoutView):
    def __init__(self, bot: CustomBot, token: str):
        super().__init__()

        self.bot = bot
        self.token = token

        lastfm = self.bot.state.lastfm

        self.link, self.confirm = (
            ui.Button(
                label="Open Last.fm login",
                url=f"http://www.last.fm/api/auth/?{urlencode({'api_key': lastfm.api_key, 'token': token})}",
                style=ButtonStyle.link,
            ),
            Confirm(self),
        )

        self.add_item(ui.ActionRow(self.link, self.confirm))


class Confirm(ui.Button):
    def __init__(self, login: Login):
        super().__init__(label="I have logged in", style=ButtonStyle.primary)

        self.login = login

    async def callback(self, interaction: Interaction):
        db = self.login.bot.state.db
        lastfm = self.login.bot.state.lastfm

        getsession = await lastfm.api(
            {"method": "auth.getsession", "token": self.login.token}
        )

        if getsession:
            key = getsession["session"]["key"]
            name = getsession["session"]["name"]

            if await db.get_user(interaction.user.id):
                await db.update_user(interaction.user.id, name, key)
            else:
                await db.create_user(interaction.user.id, name, key)

            logger.info(
                f"Last.fm '{name}' succesfully linked to discord '{interaction.user.name}"
            )

            self.label = "Success!"
            self.style = ButtonStyle.success
        else:
            logger.error(f"Last.fm failed linking to discord '{interaction.user.name}")

            self.label = "Error?"
            self.style = ButtonStyle.danger

        for child in self.login.walk_children():
            if isinstance(child, ui.Button):
                child.disabled = True

        self.login.stop()

        await interaction.response.edit_message(view=self.login)


class LastFMCog(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(
        name="link-lastfm", description="Link your Last.fm account to the radio."
    )
    @app_commands.guild_only()
    async def link_lastfm(self, interaction: Interaction):
        lastfm = self.bot.state.lastfm

        gettoken = await lastfm.api({"method": "auth.gettoken"})

        if not gettoken:
            await interaction.response.send_message(
                "Something went wrong when communicating with Last.fm, please check server logs or try again later.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            view=Login(self.bot, gettoken["token"]), ephemeral=True
        )

    @app_commands.command(
        name="unlink-lastfm", description="Unlink your Last.fm account from the radio."
    )
    @app_commands.guild_only()
    async def unlink_lastfm(self, interaction: Interaction):
        db = self.bot.state.db

        if await db.get_user(interaction.user.id):
            await db.delete_user(interaction.user.id)

            await interaction.response.send_message("Account unlinked.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "It looks like you don't have an account to unlink.", ephemeral=True
            )


async def setup(bot: CustomBot):
    await bot.add_cog(LastFMCog(bot))
