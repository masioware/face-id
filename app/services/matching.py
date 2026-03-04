import numpy as np


def l2_normalize(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-9)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = l2_normalize(a.astype(np.float32))
    b = l2_normalize(b.astype(np.float32))
    return float(np.dot(a, b))


def best_match(embedding: np.ndarray, templates: dict[str, np.ndarray]) -> tuple[str, float]:
    if not templates:
        return "unknown", -1.0

    best_name = "unknown"
    best_score = -1.0

    for name, tpl in templates.items():
        score = cosine_similarity(embedding, tpl)
        if score > best_score:
            best_name, best_score = name, score

    return best_name, best_score
