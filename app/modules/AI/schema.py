from pydantic import BaseModel


class AssistantRequest(BaseModel):
    query: str
    session_id: str | None = None


class AssistantResponse(BaseModel):
    answer: str