from typing import Optional

import cv2
import numpy as np

from app.models.identify import IdentifyError, IdentifyInput, IdentifyOutput
from app.repositories.templates import load_templates
from app.services.matching import best_match
from app.services.vision import detect_faces

DEFAULT_THRESHOLD = 0.45


def handle_frame(
    _input: IdentifyInput,
    *,
    max_frame_bytes: int,
    threshold: float = DEFAULT_THRESHOLD,
) -> IdentifyOutput:
    """
    Functional core: business rules for a single frame.
    Controller passes transport bytes in; this returns an IdentifyOutput.
    """
    if error := validate_payload_size(_input.image_bytes, max_frame_bytes=max_frame_bytes):
        return IdentifyOutput(frame_id=_input.frame_id, faces=[], error=error)

    frame = decode_image(_input.image_bytes)
    if frame is None:
        return IdentifyOutput(
            frame_id=_input.frame_id,
            faces=[],
            error=IdentifyError(code="DECODE_FAILED", message="Could not decode image bytes"),
        )

    templates = load_templates()
    faces_raw = detect_faces(frame)

    faces = [_to_face_result(f, templates=templates, threshold=threshold) for f in faces_raw]
    return IdentifyOutput(frame_id=_input.frame_id, faces=faces, error=None)


def _to_face_result(
    f: dict,
    *,
    templates: dict[str, np.ndarray],
    threshold: float,
) -> dict:
    embedding = f.get("embedding")
    if embedding is None:
        return {"bbox": f["bbox"], "name": "unknown", "score": -1.0}

    name, score = best_match(embedding, templates)
    if score < threshold:
        name = "unknown"

    return {
        "bbox": f["bbox"],
        "name": name,
        "score": score,
    }


def validate_payload_size(image_bytes: bytes, *, max_frame_bytes: int) -> Optional[IdentifyError]:
    if len(image_bytes) <= max_frame_bytes:
        return None

    return IdentifyError(code="FRAME_TOO_LARGE", message=f"Frame exceeds {max_frame_bytes} bytes")


def decode_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decode JPEG/PNG bytes into a BGR frame (OpenCV format).
    Returns None if decode fails.
    """
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(buffer, cv2.IMREAD_COLOR)
