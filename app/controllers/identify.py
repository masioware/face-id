from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import environment
from app.models.identify import IdentifyInput
from app.services.identify import handle_frame
from app.helpers.websocket import iter_ws_binary_frames, send_ws_json

router = APIRouter()

@router.websocket("/ws/identify")
async def identify(ws: WebSocket) -> None:
    await ws.accept()

    frame_id = 0
    try:
        async for payload in iter_ws_binary_frames(ws):
            out = handle_frame(
                IdentifyInput(frame_id=frame_id, image_bytes=payload),
                max_frame_bytes=environment.settings.ws_max_frame_bytes,
            )
            await send_ws_json(ws, out)
            frame_id += 1
    except WebSocketDisconnect:
        return
