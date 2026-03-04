from typing import Optional

import cv2
import numpy as np

from app.models.enroll import EnrollCommitted, EnrollProgress, EnrollState
from app.repositories.templates import upsert_template
from app.services.engine import get_face_app


def new_state(name: str) -> EnrollState:
    return EnrollState(name=name)


def decode_image(image_bytes: bytes) -> Optional[np.ndarray]:
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return frame


def handle_enroll_frame(
    *,
    state: EnrollState,
    frame_id: int,
    image_bytes: bytes,
    max_frame_bytes: int,
    min_bbox_size: int = 80,
) -> EnrollProgress:
    state.received += 1

    if len(image_bytes) > max_frame_bytes:
        return _reject(state, frame_id, reason="FRAME_TOO_LARGE")

    frame = decode_image(image_bytes)
    if frame is None:
        return _reject(state, frame_id, reason="DECODE_FAILED")

    faces = get_face_app().get(frame)

    if len(faces) != 1:
        return _reject(state, frame_id, reason="REQUIRE_SINGLE_FACE")

    face = faces[0]
    x1, y1, x2, y2 = face.bbox.astype(int).tolist()

    if (x2 - x1) < min_bbox_size or (y2 - y1) < min_bbox_size:
        return _reject(state, frame_id, reason="FACE_TOO_SMALL")

    state.embeddings.append(face.embedding.astype(np.float32))
    state.accepted += 1
    state.last_reason = None

    return _progress(state, frame_id)


def commit(*, state: EnrollState) -> EnrollCommitted:
    if not state.embeddings:
        raise ValueError("No embeddings to commit")

    template = _mean_template(state.embeddings)
    upsert_template(state.name, template)

    return EnrollCommitted(name=state.name, samples=len(state.embeddings))


def _mean_template(embeddings: list[np.ndarray]) -> np.ndarray:
    mat = np.stack(embeddings, axis=0)
    tpl = mat.mean(axis=0)
    return tpl / (np.linalg.norm(tpl) + 1e-9)


def _reject(state: EnrollState, frame_id: int, *, reason: str) -> EnrollProgress:
    state.rejected += 1
    state.last_reason = reason
    return _progress(state, frame_id)


def _progress(state: EnrollState, frame_id: int) -> EnrollProgress:
    return EnrollProgress(
        name=state.name,
        frame_id=frame_id,
        received=state.received,
        accepted=state.accepted,
        rejected=state.rejected,
        last_reason=state.last_reason,
    )
