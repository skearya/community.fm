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

    state.metadata.update(metadata)
    state.metadata_history.append((metadata, time.time()))

    logger.info(f"Received metadata update: {metadata.title}")
    return web.Response(status=200)


class InfoMessage(TypedDict):
    type: Literal["info"]
    stream: str
    metadata: dict[str, str | None] | None
    status: dict[str, Any | None] | None
    modes: list[str]


class MetadataMessage(TypedDict):
    type: Literal["metadata"]
    metadata: dict[str, str | None]


class StatusMessage(TypedDict):
    type: Literal["status"]
    status: dict[str, Any | None]


@public.get("/api/subscribe")
async def handle_get_subscribe(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]

    try:
        async with (
            sse_response(request) as resp,
            state.metadata.subscribe() as metadata_queue,
            state.status.subscribe() as status_queue,
        ):
            info: InfoMessage = {
                "type": "info",
                "stream": state.config.STREAM_BASE_URL,
                "metadata": asdict(state.metadata.value)
                if state.metadata.value
                else None,
                "status": asdict(state.status.value) if state.status.value else None,
                "modes": [mode.name for mode in state.manager.modes],
            }

            await resp.send(json.dumps(info))

            send_lock = asyncio.Lock()

            async def forward(queue: asyncio.Queue, message_type: str):
                while True:
                    payload = asdict(await queue.get())
                    message = {"type": message_type, message_type: payload}

                    async with send_lock:
                        await resp.send(json.dumps(message))

            await asyncio.gather(
                forward(metadata_queue, "metadata"),
                forward(status_queue, "status"),
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
