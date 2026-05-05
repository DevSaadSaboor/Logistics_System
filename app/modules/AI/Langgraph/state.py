from typing import TypedDict,Optional,List


class AgentState(TypedDict):
    question:str
    session_id:Optional[str]
    messages:list[dict]
    intent: Optional[str]
    context: Optional[str]
    answer:Optional[str]
