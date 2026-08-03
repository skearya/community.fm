<div align="center">

# community.fm

A configurable self-hosted radio station with powerful modes.

![GitHub Tag](https://img.shields.io/github/v/tag/skearya/community.fm)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/skearya/community.fm/build.yml)

</div>

> [!NOTE]
> community.fm does not condone piracy or unauthorized distribution of copyrighted material, and contains no code for bypassing copyright protections or obtaining unauthorized content.

|         Desktop         |         Mobile         |
| :---------------------: | :--------------------: |
| ![](assets/desktop.png) | ![](assets/mobile.png) |

...and you can also listen on VLC, MPV, IINA, Broadcasts, foobar2000, ffplay, Icecast compatible players, and a Discord bot in VCs.

## Features

- Simple & configurable
- User friendly and clean UI
- Compatible with most media players
- Track crossfades, audio normalization, blank skipping, jingles
- Discord bot with radio controlling, queuing, VC streaming

### Radio Modes

| Mode Name                    | Description                                                                |
| ---------------------------- | -------------------------------------------------------------------------- |
| Local Folder                 | shuffles through a local library of music                                  |
| Request Queue                | plays manually queued songs/albums/playlists from a URL or search          |
| YouTube Playlist             | plays songs from a YouTube playlist or a single video                      |
| Last.fm Top Tracks           | plays from users top scrobbled songs by Last.fm during a given time period |
| Discord Channel of Playlists | plays songs from a text channel of Spotify/YouTube/Apple Music playlists   |
| Incoming Livestream          | proxies an incoming livestream to the radio                                |

## Quickstart

### Step 1 - Download the required files

Create a directory of your choice (e.g. `./community-fm`) to hold the `docker-compose.yml`, `.env`, and `modes.toml` files.

```bash
mkdir ./community-fm && cd ./community-fm
```

Download `docker-compose.yml`, `example.env`, and `modes.toml.example` by running the following commands:

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/skearya/community.fm/refs/heads/main/docker-compose.yml
```

```bash
curl -o .env https://raw.githubusercontent.com/skearya/community.fm/refs/heads/main/.env.example
```

```bash
curl -o modes.toml https://raw.githubusercontent.com/skearya/community.fm/refs/heads/main/modes.toml.example
```

### Step 2 - Set the `.env` and `modes.toml` files with custom values

> .env

```bash
# URL of Icecast instance (ex: https://listen.example.com/)
ICECAST_BASE_URL=http://localhost:8000/

# Icecast passwords
ICECAST_SOURCE_PASSWORD=hackme
ICECAST_RELAY_PASSWORD=hackme
ICECAST_ADMIN_PASSWORD=hackme
LIVE_SOURCE_PASSWORD=hackme

# Directory of music for 'Local Songs' mode
LOCAL_MUSIC_DIRECTORY=?

# Token for the Discord bot (https://discord.com/developers/applications)
# DISCORD_BOT_TOKEN=?

# Last.fm API account (https://www.last.fm/api/account/create)
# LASTFM_API_KEY=?
# LASTFM_SECRET=?

# Location of 'streamrip/config.toml' (run `rip config path`)
# STREAMRIP_CONFIG_PATH=?
```

> modes.toml

```toml
[modes.local."Local Songs"]
directory = "/music"

# [modes.queue."Request Queue"]
# autoswitch = true

# [modes.youtube."DJ Mixes"]
# playlist-id = "..."

# [modes.last-fm."Weekly Top Tracks"]
# period = "7day"

# [modes.channel."Liked Songs"]
# channel-name = "liked-songs"
```

### Step 3 - Start the containers

From the directory you created in Step 1 (which should now contain your customized `.env` and `modes.toml` files), run the following command to start community.fm as a background service:

```bash
docker compose up -d
```

## Setup

- Discord Bot (strongly recommended)
- Streamrip Config (recommended for better downloads)
- Radio Mode Setup
    - Local Folder
    - Request Queue
    - YouTube Playlist
    - Last.fm Top Tracks
    - Discord Channel of Playlists
    - Incoming Livestream

### Request Queue

Plays manually queued songs/albums/playlists from a URL or search. The queue is currently only controlled by the Discord Bot. Only one request queue can be defined in the config.

#### `config.toml`

```toml
[modes.queue."Request Queue"]
# autoswitch (boolean): determines if the radio should automatically switch to the request queue mode after the current song.
autoswitch = true
```

#### Discord bot commands

- `/queue`: See the current tracks in queue
- `/queue-search`: Queue a track/album/playlist onto the radio through searching
- `/queue-url`: Queue a track/album/playlist onto the radio from a URL <sup>(qobuz/tidal/deezer/soundcloud/youtube)</sup>

### YouTube Playlist

Plays songs from a YouTube playlist or repeats a single video.

#### `config.toml`

```toml
[modes.youtube."Your Playlist Name"]
# playlist-id (string): ID of the playlist, usually after "https://www.youtube.com/playlist?list=".
playlist-id = "PLMvc7dwDCWDfeLEnRl4CREwbn1ipA8O6_"
```

### Last.fm Top Tracks

Plays from linked users top scrobbled songs by Last.fm during a given time period. Last.fm account linking is currently done through the Discord Bot with `/link-lastfm`.

A [Last.fm API account (link to create)](https://www.last.fm/api/account/create) is required to use this radio mode. The values of `Application name` and `Application description` can be anything you want. `Callback URL` and `Application homepage` can be left blank. Once you submit, set the environment variable `LASTFM_API_KEY` to "API key" and `LASTFM_SECRET` to "Shared secret".

#### `.env`

```bash
# Last.fm API account (https://www.last.fm/api/account/create)
LASTFM_API_KEY=?
LASTFM_SECRET=?
```

#### `config.toml`

```toml
[modes.last-fm."Weekly Top Tracks"]
# period ("overall" | "7day" | "1month" | "3month" | "6month" | "12month"): time period to fetch top tracks from.
period = "7day"
```

#### Discord bot commands

- `/link-lastfm`: Link your Last.fm account to the radio.
- `/unlink-lastfm`: Unlink your Last.fm account from the radio.

### Discord Channel of Playlists

Plays songs from a given Discord text channel of exported Spotify/YouTube/Apple Music playlists. Each user can only have one playlist submitted, a new playlist upload will replace the older playlist. The Discord Bot is required and needs the correct permissions to read from the given channel.

Supported playlist exporter services:

- Spotify: [Exportify](https://exportify.app/) -> Click `Export` on a playlist -> upload `.csv`
- YouTube: [Export Youtube Playlist](https://export-youtube-playlist.vercel.app/) -> Set `URL` to playlist URL -> Set `File Formats` to `CSV` -> `Export` -> upload `.csv`
- Apple Music: [Apple Music's Exporter](https://support.apple.com/guide/music/save-a-copy-of-your-playlists-mus27cd5060f/mac) -> Select playlist -> choose File > Library > Export Playlist -> upload `.xml`

#### `config.toml`

```toml
[modes.channel."Your Playlist Channel"]
# channel-name (string): name of text channel of user uploaded playlists
channel-name = "playlist-channel"
```

### Incoming Livestream

Proxies an incoming Icecast livestream to the radio. The current track will be paused when the livestream is active. A short jingle will play when switching into and out of an incoming livestream. Unlike other radio modes, livestreaming requires no configuration in `modes.toml`.

To livestream, you'll need an Icecast compatible source client, [a list can be found on Icecast's webpage](https://icecast.org/apps/). Settings for each Icecast source client vary, but generally set:

- Hostname: The IP or domain pointing to your server.
- Port: `8001` (Port exposed by Liquidsoap, not Icecast)
- Username: `streamer` or `LIVE_SOURCE_USERNAME` environment variable if set.
- Password: `LIVE_SOURCE_PASSWORD` environment variable.
- Mountpoint: `/live`

## FAQ

- Why are my track downloads of low accuracy/quality?
- How do I replace the radio webpage?
- How do I create a new radio mode?
- I have a bug to report / feature idea!
