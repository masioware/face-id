from typing import Optional

from pydantic import BaseModel, Field


class IdentifyError(BaseModel):
    code: str
    message: str


class IdentifyInput(BaseModel):
    frame_id: int
    image_bytes: bytes = Field(repr=False)


class IdentifyOutput(BaseModel):
    frame_id: int
    # Keep empty for now; you'll add bbox/name/score later
    faces: list[dict] = Field(default_factory=list)
    error: Optional[IdentifyError] = None
