#!/usr/bin/liquidsoap

BASE_URL = "http://community-fm-server:8081"

settings.encoder.metadata.export :=
  [...settings.encoder.metadata.export(), "user", "mode"]

log.file.path := "/tmp/radio.log"
log.stdout := true

# Assets
oops = single("/etc/liquidsoap/assets/oops.mp3")
loading = single("/etc/liquidsoap/assets/loading.mp3")
radio_intro = single("/etc/liquidsoap/assets/radio-intro.mp3")
stream_intro = single("/etc/liquidsoap/assets/stream-intro.mp3")

def next() =
  uri = http.get("#{BASE_URL}/next")

  if uri != "NO_NEXT" then request.create(uri) else null end
end

# Build the feed from the server
feed = request.dynamic(retry_delay=5.0, next)

# Use special loading sound when server returns "NO_NEXT"
feed = fallback(track_sensitive=false, [feed, loading])

# Skip blanks longer than 3 seconds
radio = blank.skip(max_blank=3.0, feed)

# Crossfade songs
radio = crossfade(radio)

# Server for live mixes (Icecast-compatible)
live =
  input.harbor(
    "live",
    port=8001,
    user=environment.get("LIVE_SOURCE_USERNAME"),
    password=environment.get("LIVE_SOURCE_PASSWORD"),
    replay_metadata=true,
    buffer=5.00,
    max=10.00
  )

def to_live(a, b) =
  add(normalize=false, [fade.in(b), once(stream_intro), fade.out(a)])
end

def to_radio(a, b) =
  add(normalize=false, [fade.in(b), once(radio_intro), fade.out(a)])
end

# Use live input if exists, otherwise play feed, or oops
radio =
  fallback(
    track_sensitive=false,
    transition_length=5.0,
    transitions=[to_live, to_radio],
    [live, radio, oops]
  )

# Stream it out in OGG and MP3
output.icecast(
  %mp3,
  host="community-fm-icecast",
  port=8000,
  password=environment.get("ICECAST_SOURCE_PASSWORD"),
  mount="stream.mp3",
  radio
)

output.icecast(
  %vorbis.abr(bitrate = 192, max_bitrate = 256, min_bitrate = 128),
  host="community-fm-icecast",
  port=8000,
  password=environment.get("ICECAST_SOURCE_PASSWORD"),
  mount="stream.ogg",
  radio
)

# Healthchecking
harbor.http.register.simple(
  port=8002,
  method="GET",
  "/",
  fun (_) -> http.response(content_type="text/html", data="o7")
)

# Skip current song
harbor.http.register.simple(
  port=8002,
  method="POST",
  "/skip",
  fun (_) ->
    begin
      feed.skip()

      http.response(content_type="text/plain", data="Skipped")
    end
)

# Store current song/stream metadata
last_metadata = ref([])

radio.on_metadata(
  synchronous=false,
  fun (m) ->
    begin
      last_metadata := m

      ignore(
        http.post(
          headers=[("Content-Type", "application/json")],
          data=metadata.json.stringify(m),
          "#{BASE_URL}/metadata"
        )
      )
    end
)

# Get current metadata
harbor.http.register.simple(
  port=8002,
  method="GET",
  "/metadata",
  fun (_) ->
    begin
      http.response(
        content_type="application/json", data=json.stringify(last_metadata())
      )
    end
)
