import asyncio
import json
from collections.abc import Iterable
from dataclasses import asdict

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

    return web.Response(text=await state.mode.next())


@internal.post("/metadata")
async def handle_update_metadata(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    metadata = LiquidsoapMetadata(**await request.json())
    state.metadata.update(metadata)

    logger.info(f"Received metadata update: {metadata.title}")
    return web.Response(status=200)


@public.get("/api/info")
async def handle_get_info(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]

    response = {
        "stream": state.config.STREAM_BASE_URL,
        "metadata": asdict(state.metadata.value) if state.metadata.value else None,
        "modes": [mode.name() for mode in state.modes],
    }

    return web.json_response(response)


@public.get("/api/subscribe")
async def handle_get_subscribe(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]

    try:
        async with sse_response(request) as resp, state.metadata.subscribe() as queue:
            while True:
                metadata = await queue.get()
                await resp.send(json.dumps(asdict(metadata)))
    except ClientConnectionResetError:
        pass
    except Exception:
        logger.exception("Metadata SSE failed?")

    return resp


@public.get("/")
async def handle_index(_request: web.Request) -> web.FileResponse:
    return web.FileResponse("/static/index.html")


async def spawn(
    state: State, routes: Iterable[web.AbstractRouteDef], label: str, port: int
):
    app = web.Application()
    app[STATE_KEY] = state

    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info(f"{label} HTTP server started at {site.name}")


async def start(state: State):
    # In development, /static will not contain the built frontend (use Vite's dev server).
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

    await spawn(state=state, routes=internal, label="Internal", port=8081)

    await asyncio.Event().wait()
