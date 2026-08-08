# FAQ

- [Why are my track downloads of low accuracy/quality?](#why-are-my-track-downloads-of-low-accuracyquality)
- [How do I replace the radio webpage?](#how-do-i-replace-the-radio-webpage)
- [How do I create a new radio mode?](#how-do-i-create-a-new-radio-mode)
- [I have a bug to report / feature idea!](#i-have-a-bug-to-report--feature-idea)
- [Something else?](#something-else)

## Why are my track downloads of low accuracy/quality?

> [Streamrip Config Setup](setup.md#streamrip-config)
>
> community.fm uses [streamrip](https://github.com/nathom/streamrip) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download tracks. By default, streamrip can only download SoundCloud tracks (without drm). You can also download from Qobuz, Tidal, and Deezer using a streamrip config with the respective login keys. Using any one of these services greatly improves search quality.

If you aren't using Qobuz, Tidal, or Deezer or have keys to them (you may be able to find them online), you can still make a free [Deezer account](https://account.deezer.com/en-us/signup/) and still greatly improve download accuracy and quality.

## How do I replace the radio webpage?

`community-fm-server` will serve files that are in the container's `/static` directory and serve `/static/index.html` at the root. By default, community.fm's frontend build lives there. You can override the served webpage by creating a bind mount from your frontend directory to `/static`.

The APIs that the community.fm default frontend uses to display the current track, history, listeners and such are currently undocumented (though, [open source](https://github.com/skearya/community.fm/tree/main/web)).

That being said, here's an (extremely) minimal example of a functional community.fm frontend.

<details>

<summary><code>index.html</code></summary>

```html
<!doctype html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>custom.fm</title>
	</head>
	<body>
		<main>
			<pre id="info"></pre>
			<audio id="audio" src="" controls></audio>
			<img id="cover" src="" alt="" />
		</main>

		<script>
			const infoElement = document.querySelector("#info");
			const audioElement = document.querySelector("#audio");
			const coverElement = document.querySelector("#cover");

			let state;

			const eventSource = new EventSource("/api/subscribe");

			eventSource.addEventListener("message", (event) => {
				const message = JSON.parse(event.data);

				switch (message.type) {
					case "info":
						state = message;
						break;
					case "liquidsoap":
						state.history.push(state.liquidsoap);
						state.liquidsoap = message.data;
						break;
					case "icecast":
						state.icecast = message.data;
						break;
				}

				infoElement.textContent = JSON.stringify(state.liquidsoap, null, 2);
				audioElement.src = `${state.stream}stream.ogg`;
				coverElement.src = `/api/cover/${state.liquidsoap.id}`;
			});
		</script>
	</body>
</html>
```

</details>

If you have a complex build process, you can create your own Dockerfile that extends from `ghcr.io/skearya/community.fm-server`, builds a static frontend in `/static`, and use that in your compose.

## How do I create a new radio mode?

TODO

## I have a bug to report / feature idea!

https://github.com/skearya/community.fm/issues

## Something else?

Contact me on Discord @ `squisket` or anywhere else you can find me.
