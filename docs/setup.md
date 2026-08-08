# Setup

- Radio Modes
    - [Local Songs](#local-songs)
    - [Request Queue](#request-queue)
    - [YouTube Playlist](#youtube-playlist)
    - [Last.fm Top Tracks](#lastfm-top-tracks)
    - [Discord Channel of Playlists](#discord-channel-of-playlists)
    - [Incoming Livestream](#incoming-livestream)
- [Discord Bot](#discord-bot)
- [Streamrip Config](#streamrip-config)
- [Reverse Proxying](#reverse-proxying)

## Local Songs

Shuffles through a local library of music.

The local library needs to be mounted to a path of your choice in **both** the `community-fm-server` and `community-fm-liquidsoap` docker containers. In the quickstart `docker-compose.yml`, there is a bind mount made for you that mounts `${LOCAL_MUSIC_DIRECTORY}` to `/music` on both containers. You can make more bind mounts yourself and use them in `modes.toml`.

To enable this mode, add `[modes.local."Your Name"]` to `config.toml` with these options:

- `directory` = absolute path **in the docker container accesible by `community-fm-server` and `community-fm-liquidsoap`**.

#### Example `config.toml`

```toml
[modes.local."My Songs"]
directory = "/music"

[modes.local."My Mixes"]
directory = "/mixes"
```

## Request Queue

Plays manually queued songs/albums/playlists from a URL or search. Controlling the queue is done through the [Discord bot](#discord-bot). Only one request queue can be defined in the config.

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

## YouTube Playlist

Plays items from a YouTube playlist or repeats a single video.

To enable this mode, add `[modes.youtube."Your Name"]` to `config.toml` with these options:

- `playlist-id` = ID to a YouTube playlist, usually found after `youtube.com/playlist?list=`.

#### Example `config.toml`

```toml
[modes.youtube."Cool Sets"]
playlist-id = "PLMvc7dwDCWDfeLEnRl4CREwbn1ipA8O6_"
```

## Last.fm Top Tracks

Plays linked users top scrobbled songs from Last.fm during a given time period. Last.fm account linking is currently done through the [Discord bot](#discord-bot) with `/link-lastfm`.

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

## Discord Channel of Playlists

Plays songs from a given Discord text channel of exported Spotify/YouTube/Apple Music playlists. Each user can only have one playlist submitted, a new playlist uploaded will replace the older playlist. The [Discord bot](#discord-bot) is required and needs the correct permissions to read from the given channel.

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

## Incoming Livestream

Proxies an incoming Icecast livestream to the radio. The current mode will be paused when the livestream is active and a short jingle will play when switching into and out of an livestream.

Unlike other radio modes, livestreaming requires no configuration in `modes.toml`.

To livestream, you'll need an Icecast compatible source client, [a list can be found on Icecast's webpage](https://icecast.org/apps/). I recommend [Mixxx](https://mixxx.org/) or [butt](https://danielnoethen.de/butt/). Settings for each client vary, but generally set:

- Hostname: The IP or domain pointing to your server.
- Port: `8001` (Port exposed by Liquidsoap, not Icecast)
- Username: `streamer` or `LIVE_SOURCE_USERNAME` environment variable if set.
- Password: `LIVE_SOURCE_PASSWORD` environment variable.
- Mountpoint: `/live`

## Discord Bot

The Discord bot lets you stream the radio to voice channels, change the radio mode, skip songs, queue music, and more. It is a prerequisite to the [Request Queue](#request-queue), [Last.fm Top Tracks](#lastfm-top-tracks), and [Discord Channel of Playlists](#discord-channel-of-playlists) radio modes.

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" in the top right corner.
3. Enter a name for your application and accept the Developer ToS.
4. Click "Create".
5. In the left sidebar, click "Bot".
6. Under "Privileged Gateway Intents" enable "Message Content Intent".
7. Under the "Token" section, click "Reset Token". In `.env` set `DISCORD_BOT_TOKEN` to the new token.
8. In the left sidebar, click "OAuth2".
9. Under "Client Information", copy your "Client ID" and replace `YOUR_CLIENT_ID` in the URL below with the Client ID, visit it and invite the bot.

```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2150713408&integration_type=0&scope=bot
```

Restart with `docker compose up -d`.

## Streamrip Config

community.fm uses [streamrip](https://github.com/nathom/streamrip) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download tracks. By default, streamrip can only download SoundCloud tracks (without drm). You can also download from Qobuz, Tidal, and Deezer using a streamrip config with the respective login keys. Using any one of these services greatly improves search quality. Refer to the official [streamrip wiki](https://github.com/nathom/streamrip/wiki) on how to install and configure it.

Once you have a streamrip config, set `STREAMRIP_CONFIG_PATH` in `.env` to the path to your local streamrip config, which you can find by running `rip config path`. Additionally, in your `docker-compose.yml`, uncomment the config bind mount on `comunnity-fm-server` below.

```yaml
# Uncomment to use a streamrip config from `rip config path` for better downloads:
# - ${STREAMRIP_CONFIG_PATH}:/root/.config/streamrip/config.toml:ro
```

Restart with `docker compose up -d`.

## Reverse Proxying

These instructions are for [Caddy](https://caddyserver.com/) specifically, but should be useful to anyone using another reverse proxy.

1. Remove the `8080:8080` and `8000:8000` port mappings from `community-fm-server` and `community-fm-icecast` to stop exposing them directly.

> [!NOTE]
> You have to leave `community-fm-liquidsoap`'s `8001:8001` port mapping open if you want to accept [incoming livestreams](#incoming-livestream) as Caddy only proxies HTTP traffic.

2. In your `Caddyfile`, setup two `reverse_proxy` rules for `community-fm-server:8080` (website + api) and `community-fm-icecast:8000` (audio stream).

3. In your `.env`, set `ICECAST_BASE_URL` to wherever `community-fm-icecast` is reverse proxied, for example `https://listen.example.com/`

#### Example `Caddyfile`

```Caddyfile
radio.example.com {
	reverse_proxy community-fm-server:8080
}

listen.example.com {
	reverse_proxy community-fm-icecast:8000
}
```
