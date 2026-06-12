from dataclasses import dataclass
from os import environ


@dataclass
class Config:
    DEV = environ.get("MODE", "production") == "development"
    PROD = environ.get("MODE", "production") == "production"

    STREAM_BASE_URL = environ["STREAM_BASE_URL"]
    DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
    DISCORD_TEST_GUILD = environ.get("DISCORD_TEST_GUILD", None)
    LASTFM_API_KEY = environ.get("LASTFM_API_KEY", None)
    LASTFM_SECRET = environ.get("LASTFM_SECRET", None)

    CONFIG_FILEPATH = "/data/config.toml"
    DATABASE_FILEPATH = "/data/community-fm.db"
    PLS_DOWNLOAD_DIRECTORY = "/downloads"

    ICECAST_BASE_URL = "http://community-fm-icecast:8000"
    LIQUIDSOAP_BASE_URL = "http://community-fm-liquidsoap:8002"
