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

...and you can also listen on [VLC](https://www.videolan.org/), [MPV](https://mpv.io/), [IINA](https://iina.io/), [Broadcasts](https://apps.apple.com/us/app/broadcasts/id1469995354), [foobar2000](https://www.foobar2000.org/), [ffplay](https://ffmpeg.org/ffplay.html), [Icecast compatible players](https://icecast.org/apps/#players), and a Discord bot in VCs.

## Features

- Simple & configurable
- User friendly and clean UI
- Compatible with most media players
- Track crossfades, audio normalization, blank skipping, jingles
- Discord bot with radio controlling, queuing, VC streaming

### Radio Modes

| Mode Name                    | Description                                                                |
| ---------------------------- | -------------------------------------------------------------------------- |
| Local Songs                  | shuffles through a local library of music                                  |
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

### Step 2 - Edit the `.env` and `modes.toml` files with custom values

Radio modes are enabled in `modes.toml`, [see the full list of supported modes here](). You can enable any combination of modes, including multiple instances of the same mode. Using a mode looks like so:

```toml
[modes.(type)."(name)"]
# options...
```

For example, this creates an instance of the "Local Songs" (`local`) mode named "Hardstyle Tracks".

```toml
[modes.local."Hardstyle Tracks"]
directory = "/music/hardsyle"
```

community.fm needs at least one radio mode active in order to start. The "Local Songs" radio mode has already been enabled in the `modes.toml`, to use it **set `LOCAL_MUSIC_DIRECTORY` in `.env` to a folder on your machine with audio files**.

> If you don't want to enable the "Local Songs" mode, you can remove the two `${LOCAL_MUSIC_DIRECTORY}:/music:ro` bind mounts in the `docker-compose.yml` and enable another mode instead.

#### `.env`

```bash
# URL of Icecast instance (ex: http://localhost:8000/ or https://listen.example.com/)
ICECAST_BASE_URL=http://localhost:8000/

# Passwords (MUST BE CHANGED from "hackme" on a public instance)
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

> [!CAUTION]
> The `ICECAST_SOURCE_PASSWORD`, `ICECAST_RELAY_PASSWORD`, `ICECAST_ADMIN_PASSWORD`, `LIVE_SOURCE_PASSWORD` variables **must be replaced** from the default of "hackme" on a public instance. You can generate passwords by running `openssl rand -hex 16`.

#### `modes.toml`

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
    - Local Songs
    - Request Queue
    - YouTube Playlist
    - Last.fm Top Tracks
    - Discord Channel of Playlists
    - Incoming Livestream
- Reverse Proxying

### Local Songs

Shuffles through a local library of music.

The local library needs to be mounted to the `community-fm-server` and `community-fm-liquidsoap` docker containers. In the quickstart `docker-compose.yml`, there is a bind mount made for you that mounts `${LOCAL_MUSIC_DIRECTORY}` to `/music` on **both** containers. You can make more mounts yourself and reference them in `modes.toml`.

To enable this mode, add `[modes.local."Your Name"]` to `config.toml` with these options:

- `directory` = absolute path **in the docker container accesible by `community-fm-server` and `community-fm-liquidsoap`**.F

#### Example `config.toml`

```toml
[modes.local."My Songs"]
directory = "/music"

[modes.local."My Mixes"]
directory = "/mixes"
```

### Request Queue

Plays manually queued songs/albums/playlists from a URL or search. Controlling the queue is done through the Discord Bot. Only one request queue can be defined in the config.

To enable this mode, add `[modes.queue."Your Name"]` to `config.toml` with these options:

- `autoswitch` = if the radio should automatically switch to the request queue mode after the current song.

#### Example `config.toml`

```toml
[modes.queue."Request Queue"]
autoswitch = true
```

#### Discord bot commands

- `/queue`: See the current tracks in queue
- `/queue-search`: Queue a track/album/playlist onto the radio through searching
- `/queue-url`: Queue a track/album/playlist onto the radio from a URL <sup>(qobuz/tidal/deezer/soundcloud/youtube)</sup>

### YouTube Playlist

Plays items from a YouTube playlist or repeats a single video.

To enable this mode, add `[modes.youtube."Your Name"]` to `config.toml` with these options:

- `playlist-id` = ID to a YouTube playlist, usually found after `youtube.com/playlist?list=`.

#### Example `config.toml`

```toml
[modes.youtube."Cool Sets"]
playlist-id = "PLMvc7dwDCWDfeLEnRl4CREwbn1ipA8O6_"
```

### Last.fm Top Tracks

Plays linked users top scrobbled songs from Last.fm during a given time period. Last.fm account linking is currently done through the Discord Bot with `/link-lastfm`.

A [Last.fm API account (link to create)](https://www.last.fm/api/account/create) is required to use this radio mode. The values of `Application name` and `Application description` can be anything. `Callback URL` and `Application homepage` can be left blank. Once you submit, set the environment variable `LASTFM_API_KEY` to "API key" and `LASTFM_SECRET` to "Shared secret".

#### Required `.env`

```bash
# Last.fm API account (https://www.last.fm/api/account/create)
LASTFM_API_KEY=?
LASTFM_SECRET=?
```

To enable this mode, add `[modes.last-fm."Your Name"]` to `config.toml` with these options:

- `period` = time period to fetch top tracks from, either `"overall" | "7day" | "1month" | "3month" | "6month" | "12month"`.

#### Example `config.toml`

```toml
[modes.last-fm."Weekly Top Tracks"]
period = "7day"

[modes.last-fm."Yearly Top Tracks"]
period = "12month"
```

#### Discord bot commands

- `/link-lastfm`: Link your Last.fm account to the radio.
- `/unlink-lastfm`: Unlink your Last.fm account from the radio.

### Discord Channel of Playlists

Plays songs from a given Discord text channel of exported Spotify/YouTube/Apple Music playlists. Each user can only have one playlist submitted, a new playlist uploaded will replace the older playlist. The Discord Bot is required and needs the correct permissions to read from the given channel.

How to upload a playlist:

- Spotify: [Exportify](https://exportify.app/) -> Click `Export` on a playlist -> upload `.csv`
- YouTube: [Export Youtube Playlist](https://export-youtube-playlist.vercel.app/) -> Set `URL` to playlist URL -> Set `File Formats` to `CSV` -> `Export` -> upload `.csv`
- Apple Music: [Apple Music's Exporter](https://support.apple.com/guide/music/save-a-copy-of-your-playlists-mus27cd5060f/mac) -> Select playlist -> choose File > Library > Export Playlist -> upload `.xml`

To enable this mode, add `[modes.channel."Your Name"]` to `config.toml` with these options:

- `channel-name` = name of text channel of user uploaded playlists.

#### Example `config.toml`

```toml
[modes.channel."Liked Songs"]
channel-name = "liked-songs-playlists"
```

### Incoming Livestream

Proxies an incoming Icecast livestream to the radio. The current mode will be paused when the livestream is active and a short jingle will play when switching into and out of an livestream.

Unlike other radio modes, livestreaming requires no configuration in `modes.toml`.

To livestream, you'll need an Icecast compatible source client, [a list can be found on Icecast's webpage](https://icecast.org/apps/). I recommend [Mixxx](https://mixxx.org/) or [butt](https://danielnoethen.de/butt/). Settings for each client vary, but generally set:

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
