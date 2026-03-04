from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.models.enroll import EnrollAck, EnrollWsMessage
from app.services.enroll import commit, handle_enroll_frame, new_state
from app.config.environment import settings

router = APIRouter()


@router.websocket("/ws/enroll")
async def ws_enroll(ws: WebSocket, name: str) -> None:
    await ws.accept()

    state = new_state(name=name)
    await ws.send_text(EnrollAck(name=name).model_dump_json())

    frame_id = 0

    try:
        while True:
            msg = await ws.receive()

            # Binary frames
            if (payload := msg.get("bytes")) is not None:
                out = handle_enroll_frame(
                    state=state,
                    frame_id=frame_id,
                    image_bytes=payload,
                    max_frame_bytes=settings.ws_max_frame_bytes,
                )
                await ws.send_text(out.model_dump_json())
                frame_id += 1
                continue

            # Optional text commands: commit/cancel
            if (text := msg.get("text")) is not None:
                cmd = EnrollWsMessage.model_validate_json(text)

                if cmd.type == "cancel":
                    await ws.close(code=status.WS_1000_NORMAL_CLOSURE)
                    return

                if cmd.type == "commit":
                    result = commit(state=state)
                    await ws.send_text(result.model_dump_json())
                    await ws.close(code=status.WS_1000_NORMAL_CLOSURE)
                    return

    except WebSocketDisconnect:
        return
