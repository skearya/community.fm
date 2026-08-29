#!/usr/bin/liquidsoap

BASE_URL = "http://community-fm-server:8081"

settings.encoder.metadata.export :=
  [...settings.encoder.metadata.export(), "user", "avatar", "mode", "playcount"]

log.file.path := "/tmp/radio.log"
log.stdout := true

def asset(title, uri, ~mode="") =
  single(
    if
      mode == ""
    then
      'annotate:title="#{title}",artist="community.fm":#{uri}'
    else
      'annotate:title="#{title}",artist="community.fm",mode="#{mode}":#{uri}'
    end
  )
end

# Assets
fatal_error_sound =
  asset("Error", "/etc/liquidsoap/assets/fatal-error.mp3", mode="Error")

stream_intro_sound =
  asset(
    "Starting Stream",
    "/etc/liquidsoap/assets/stream-intro.mp3"
  )

radio_intro_sound =
  asset(
    "Starting Radio",
    "/etc/liquidsoap/assets/radio-intro.mp3"
  )

loading_sound =
  asset("Loading", "/etc/liquidsoap/assets/loading.mp3", mode="Loading")

def next() =
  uri = http.get("#{BASE_URL}/next")

  if uri == "LOADING" then null else request.create(uri) end
end

# Build the feed from the server
feed =
  request.dynamic(
    prefetch=1,
    retry_delay=0.1,
    fun () ->
      begin
        uri = http.get("#{BASE_URL}/next")

        if uri == "LOADING" then null else request.create(uri) end
      end
  )

# Use special loading sound when server returns "LOADING"
radio =
  fallback(
    track_sensitive=false,
    transition_length=5.0,
    transitions=[cross.simple, cross.simple],
    [feed, loading_sound]
  )

# Eat blanks longer than 10 seconds
radio = blank.eat(max_blank=10.0, radio)

# Crossfade songs
radio = crossfade(radio)

# Server for livestreams (Icecast-compatible)
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

# Make the livestream unavailable when streaming blank
live = blank.strip(max_blank=10.0, live)

# Add mode = "Livestream" metadata to livestream
live = metadata.map(fun (_) -> begin [("mode", "Livestream")] end, live)

def to_live(a, b) =
  add(normalize=false, [cross.simple(a, b), once(stream_intro_sound)])
end

def to_radio(a, b) =
  add(normalize=false, [cross.simple(a, b), once(radio_intro_sound)])
end

# Use livestream if exists, otherwise play feed, or fatal error sound
radio =
  fallback(
    track_sensitive=false,
    transition_length=5.0,
    transitions=[to_live, to_radio],
    [live, radio, fatal_error_sound]
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

# Clear `request.dynamic`s internal queue
harbor.http.register.simple(
  port=8002,
  method="POST",
  "/clear",
  fun (_) ->
    begin
      list.iter(request.destroy, feed.queue())
      feed.set_queue([])

      http.response(content_type="text/plain", data="Cleared")
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
