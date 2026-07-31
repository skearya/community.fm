import asyncio
import json
import uuid
from collections.abc import Iterable

from aiohttp import ClientConnectionResetError, web
from aiohttp_sse import sse_response
from loguru import logger
from models import (
    IcecastMessage,
    InfoMessage,
    LiquidsoapEntry,
    LiquidsoapMessage,
    LiquidsoapMetadata,
)
from state import State

STATE_KEY = web.AppKey("STATE_KEY", State)

public = web.RouteTableDef()
internal = web.RouteTableDef()


@internal.get("/next")
async def handle_next(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    next = state.manager.next()

    return web.Response(text=next)


@internal.post("/metadata")
async def handle_update_metadata(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    body = await request.json()
    assert isinstance(body, dict)

    cover = body.pop("cover", None)
    metadata = LiquidsoapMetadata(**body)
    entry = LiquidsoapEntry(metadata, cover)

    state.history.append(state.liquidsoap.value)
    state.liquidsoap.update(entry)

    logger.info(f"Received metadata update: {metadata.title}")
    return web.Response(status=200)


@public.get("/api/subscribe")
async def handle_get_subscribe(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]

    try:
        async with (
            sse_response(request) as resp,
            state.icecast.subscribe() as icecast_queue,
            state.liquidsoap.subscribe() as liquidsoap_queue,
        ):
            send_lock = asyncio.Lock()

            async def send(message: InfoMessage | LiquidsoapMessage | IcecastMessage):
                async with send_lock:
                    await resp.send(json.dumps(message))

            await send(
                {
                    "type": "info",
                    "stream": state.config.ICECAST_PUBLIC_BASE_URL,
                    "modes": [mode.name for mode in state.manager.modes],
                    "icecast": state.icecast.value,
                    "liquidsoap": state.liquidsoap.value.serializable(),
                    "history": [entry.serializable() for entry in state.history],
                }
            )

            async def forward_icecast(queue: asyncio.Queue[object]):
                while True:
                    data = await queue.get()

                    await send({"type": "icecast", "data": data})

            async def forward_liquidsoap(queue: asyncio.Queue[LiquidsoapEntry]):
                while True:
                    data = await queue.get()

                    await send({"type": "liquidsoap", "data": data.serializable()})

            await asyncio.gather(
                forward_icecast(icecast_queue),
                forward_liquidsoap(liquidsoap_queue),
            )
    except ClientConnectionResetError:
        pass
    except Exception:
        logger.exception("Subscribe SSE failed?")

    return resp


@public.get("/api/cover/{id}")
async def handle_cover(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    if not (id_str := request.match_info.get("id")):
        return web.Response(status=400)

    id = uuid.UUID(id_str)

    if id == state.liquidsoap.value.id:
        entry = state.liquidsoap.value
    else:
        entry = next((entry for entry in state.history if entry.id == id), None)

    if not entry or not entry.cover:
        return web.Response(status=404)

    mime, bytes = entry.cover

    return web.Response(body=bytes, content_type=mime)


@public.get("/")
async def handle_index(_request: web.Request) -> web.FileResponse:
    return web.FileResponse("/static/index.html")


async def spawn(
    state: State,
    routes: Iterable[web.AbstractRouteDef],
    label: str,
    port: int,
    client_max_size: int = 1024**2,
):
    app = web.Application(client_max_size=client_max_size)
    app[STATE_KEY] = state

    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info(f"{label} HTTP server started at {site.name}")


async def start(state: State):
    # In development, /static will not contain the built frontend (use Vite's dev server instead).
    # In production, the server will be serving the static frontend.
    if state.config.DEV:
        await spawn(
            state=state,
            routes=public,
            label="Public (Development)",
            port=8080,
        )
    else:
        await spawn(
            state=state,
            routes=[web.get("/", handle_index), web.static("/", "/static"), *public],
            label="Public (Production)",
            port=8080,
        )

    await spawn(
        state=state,
        routes=internal,
        label="Internal",
        port=8081,
        # Let liquidsoap send ~50MB requests due to large coverart.
        # Excessive, but better safe than sorry.
        client_max_size=1024**2 * 50,
    )

    await asyncio.Event().wait()
