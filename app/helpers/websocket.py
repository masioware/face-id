
from collections.abc import AsyncIterator
from typing import Any

from fastapi import WebSocket


async def iter_ws_binary_frames(ws: WebSocket) -> AsyncIterator[bytes]:
    """
    Yields only binary messages (JPEG/PNG bytes). Ignores non-binary messages.
    """
    while True:
        msg = await ws.receive()
        payload = msg.get("bytes")
        if payload is not None:
            yield payload


async def send_ws_json(ws: WebSocket, model: Any) -> None:
    """
    Sends a Pydantic model as JSON text.
    """
    await ws.send_text(model.model_dump_json())
