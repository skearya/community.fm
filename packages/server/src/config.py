from os import environ
from dataclasses import dataclass


@dataclass
class Config:
    STREAM_BASE_URL = environ["STREAM_BASE_URL"]
    DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
    DISCORD_TEST_GUILD = environ.get("DISCORD_TEST_GUILD", None)
    YOUTUBE_PLAYLIST_ID = environ.get("YOUTUBE_PLAYLIST_ID", None)

    LOCAL_MUSIC_DIRECTORY = "/music"
    PLS_DOWNLOAD_DIRECTORY = "/downloads"
    PLS_DATABASE_FILEPATH = "/data/pls.db"

    ICECAST_BASE_URL = "http://icecast:8000"
    LIQUIDSOAP_BASE_URL = "http://liquidsoap:8002"
