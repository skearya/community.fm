from dataclasses import dataclass
from os import environ


@dataclass
class Config:
    DEV = environ.get("MODE", "production") == "development"
    PROD = environ.get("MODE", "production") == "production"

    STREAM_BASE_URL = environ["STREAM_BASE_URL"]
    DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
    DISCORD_TEST_GUILD = environ.get("DISCORD_TEST_GUILD", None)
    YOUTUBE_PLAYLIST_ID = environ.get("YOUTUBE_PLAYLIST_ID", None)

    LOCAL_MUSIC_DIRECTORY = "/music"
    PLS_DOWNLOAD_DIRECTORY = "/downloads"
    PLS_DATABASE_FILEPATH = "/data/pls.db"

    ICECAST_BASE_URL = "http://community-fm-icecast:8000"
    LIQUIDSOAP_BASE_URL = "http://community-fm-liquidsoap:8002"
