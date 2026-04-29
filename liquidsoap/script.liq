#!/usr/bin/liquidsoap

default_settings = settings.encoder.metadata.export()
settings.encoder.metadata.export := [...default_settings, "user"]

log.file.path := "/tmp/radio.log"
log.stdout := true

# Assets
oops = single("/etc/liquidsoap/assets/oops.mp3")
radio_intro = single("/etc/liquidsoap/assets/radio-intro.mp3")
stream_intro = single("/etc/liquidsoap/assets/stream-intro.mp3")

def next() =
  uri = http.get("http://server:8080/next")

  if uri != "NO_NEXT" then request.create(uri) else null end
end

# Build the feed from the server
radio = request.dynamic(retry_delay=5.0, next)

# Skip blanks longer than 3 seconds
radio = blank.skip(max_blank=3.0, radio)

# Crossfade songs
radio = crossfade(radio)

# Server for live mixes (Icecast-compatible)
live =
  input.harbor(
    "live",
    port=8001,
    user="miku",
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

# Use live input if exists, otherwise play /music, or oops.mp3
radio =
  fallback(
    track_sensitive=false,
    transition_length=15.0,
    transitions=[to_live, to_radio],
    [live, radio, oops]
  )

# Stream it out in OGG and MP3
output.icecast(
  %mp3,
  host="icecast",
  port=8000,
  password=environment.get("ICECAST_SOURCE_PASSWORD"),
  mount="stream.mp3",
  radio
)

output.icecast(
  %vorbis.abr(bitrate = 192, max_bitrate = 256, min_bitrate = 128),
  host="icecast",
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

# Store current song/stream metadata
last_metadata = ref([])
radio.on_metadata(
  synchronous=false,
  fun (m) ->
    begin
      last_metadata := m

      headers = [("Content-Type", "application/json")]
      ignore(
        http.post(
          headers=headers,
          data=metadata.json.stringify(m),
          "http://server:8080/metadata"
        )
      )
    end
)

# Serve current song/stream metadata
harbor.http.register.simple(
  port=8002,
  method="GET",
  "/metadata",
  fun (_) ->
    begin
      data = last_metadata()

      headers = [("Access-Control-Allow-Origin", "*")]
      http.response(
        headers=headers,
        content_type="application/json",
        data=metadata.json.stringify(data)
      )
    end
)
