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
    state.metadata = LiquidsoapMetadata(**await request.json())

    for queue in state.metadata_listeners:
        await queue.put(state.metadata)

    logger.info(f"Received metadata update: {state.metadata.title}")
    return web.Response(status=200)


@public.get("/metadata")
async def handle_get_metadata(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]
    queue = asyncio.Queue()

    state.metadata_listeners.add(queue)

    try:
        async with sse_response(request) as resp:
            if metadata := state.metadata:
                await resp.send(json.dumps(asdict(metadata)))

            while True:
                metadata = await queue.get()
                await resp.send(json.dumps(asdict(metadata)))
    except ClientConnectionResetError:
        pass
    except Exception:
        logger.exception("Metadata SSE failed?")
    finally:
        state.metadata_listeners.remove(queue)

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
    await spawn(
        state,
        [web.get("/", handle_index), web.static("/", "/static"), *public],
        "Public",
        8080,
    )

    await spawn(state, internal, "Internal", 8081)

    await asyncio.Event().wait()
