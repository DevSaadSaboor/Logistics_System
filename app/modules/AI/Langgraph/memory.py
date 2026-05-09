from sqlalchemy import select

from app.modules.AI.model import ChatHistory

async def save_messages(db,session_id:str,role:str,content:str):
    messages = ChatHistory(session_id = session_id , role = role , content = content)
    db.add(messages)
    await db.commit()

async def load_messages(db,session_id:str):
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        {
        "role": m.role,
        "content": m.content
        }
        for m in messages
    ]


