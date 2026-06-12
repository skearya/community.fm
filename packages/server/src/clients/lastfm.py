from hashlib import md5
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from loguru import logger

if TYPE_CHECKING:
    from state import State

LASTFM_BASE_URL = "https://ws.audioscrobbler.com"


class LastFM:
    def __init__(self, state: State, api_key: str, secret: str):
        self.state = state
        self.api_key = api_key
        self.secret = secret

    async def api(self, params: dict[str, str]) -> dict | None:
        params["format"] = "json"
        params["api_key"] = self.api_key
        params["api_sig"] = md5(
            (
                "".join([f"{k}{v}" for k, v in sorted(params.items()) if k != "format"])
                + self.secret
            ).encode()
        ).hexdigest()

        async with self.state.session.get(
            f"{LASTFM_BASE_URL}/2.0/?{urlencode(params)}"
        ) as response:
            data = await response.json()

            if code := data.get("error"):
                logger.error(f"Last.fm API error: {code}, {data.get('message')}")
                return None

            return data
