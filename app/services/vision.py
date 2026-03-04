from insightface.app import FaceAnalysis
import numpy as np


_face_app: FaceAnalysis | None = None


def get_face_app() -> FaceAnalysis:
    global _face_app

    if _face_app is None:
        _face_app = FaceAnalysis(
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )
        _face_app.prepare(ctx_id=0, det_size=(640, 640))

    return _face_app


def detect_faces(frame: np.ndarray) -> list[dict]:
    app = get_face_app()
    faces = app.get(frame)

    return [
        {
            "bbox": face.bbox.astype(int).tolist(),
            "embedding": face.embedding,  # ainda não usamos
        }
        for face in faces
    ]
