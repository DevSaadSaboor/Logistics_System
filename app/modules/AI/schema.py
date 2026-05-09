from pydantic import BaseModel, Field
from typing import Optional


class AssistantRequest(BaseModel):
    query: str = Field(..., examples=["Where is my shipment?"])
    # Optional: omit it to start a new chat session.
    session_id: Optional[str] = Field(
        default=None,
        examples=[None, "f3f2c8b6-3b72-4e7f-9f8c-2d1c0f9c7f2a"],
    )


class AssistantResponse(BaseModel):
    session_id :str
    answer: str