import asyncio
import json
import time
from collections.abc import Iterable
from dataclasses import asdict
from typing import Any, Literal, TypedDict

from aiohttp import ClientConnectionResetError, web
from aiohttp_sse import sse_response
from loguru import logger
from models import LiquidsoapMetadata
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

    metadata = LiquidsoapMetadata(**await request.json())

    state.liquidsoap.update(metadata)
    state.history.append((metadata, time.time()))

    logger.info(f"Received metadata update: {metadata.title}")
    return web.Response(status=200)


class InfoMessage(TypedDict):
    type: Literal["info"]
    stream: str
    modes: list[str]
    history: list[tuple[dict[str, Any], int | float]]
    liquidsoap: dict[str, Any]
    icecast: object


class LiquidsoapMessage(TypedDict):
    type: Literal["liquidsoap"]
    liquidsoap: dict[str, Any]


class IcecastMessage(TypedDict):
    type: Literal["icecast"]
    icecast: object


@public.get("/api/subscribe")
async def handle_get_subscribe(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]

    try:
        async with (
            sse_response(request) as resp,
            state.liquidsoap.subscribe() as liquidsoap_queue,
            state.icecast.subscribe() as icecast_queue,
        ):
            info: InfoMessage = {
                "type": "info",
                "stream": state.config.STREAM_BASE_URL,
                "modes": [mode.name for mode in state.manager.modes],
                "history": [(asdict(track), time) for track, time in state.history],
                "liquidsoap": asdict(state.liquidsoap.value),
                "icecast": state.icecast.value,
            }

            await resp.send(json.dumps(info))

            send_lock = asyncio.Lock()

            async def forward(queue: asyncio.Queue, type: str, dataclass: bool):
                while True:
                    data = await queue.get()
                    message = {"type": type, type: asdict(data) if dataclass else data}

                    async with send_lock:
                        await resp.send(json.dumps(message))

            await asyncio.gather(
                forward(liquidsoap_queue, "liquidsoap", True),
                forward(icecast_queue, "icecast", False),
            )
    except ClientConnectionResetError:
        pass
    except Exception:
        logger.exception("Subscribe SSE failed?")

    return resp


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
