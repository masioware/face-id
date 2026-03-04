from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class EnrollError(BaseModel):
    code: str
    message: str


class EnrollProgress(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: Literal["progress"] = "progress"
    name: str
    frame_id: int
    received: int
    accepted: int
    rejected: int
    last_reason: Optional[str] = None


class EnrollCommitted(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: Literal["committed"] = "committed"
    name: str
    samples: int


class EnrollAck(BaseModel):
    type: Literal["ack"] = "ack"
    name: str


class EnrollWsMessage(BaseModel):
    type: Literal["commit", "cancel"]


class EnrollState(BaseModel):
    """
    Per-connection mutable state (kept in memory during the WS session).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    received: int = 0
    accepted: int = 0
    rejected: int = 0
    last_reason: Optional[str] = None
    embeddings: list[np.ndarray] = Field(default_factory=list)
