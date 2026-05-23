import asyncio
import os
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.AI.categorizer import ShipmentCategorizer
from app.modules.shipments.repository import ShipmentRespository

_api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=_api_key) if _api_key else None


class ShipmentAiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShipmentRespository(db)
        api_key = os.getenv("OPENAI_API_KEY")   
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_embedding(self, text: str):
        if client is None:
            return None
        try:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            print("❌ EMBEDDING ERROR:", e)
            return None

    async def categorizer_and_update_shipment(self, shipment_id: UUID, tenant_id, description: str):

        print("AI SERVICE TRIGGERED")
        categorizer = ShipmentCategorizer()
        try:
            # print("➡️ Running categorizer...")
            result = await asyncio.to_thread(categorizer.categorize, description)
            category = result.category
            confidence = result.confidence
            # print("➡️ Generating embedding...")
            embedding = await self.generate_embedding(description)
    
        except Exception as e :
            print("❌ AI ERROR:", e)
            category = "other"
            confidence = 0.0
            embedding = None
            # print("➡️ Saving to DB...")

        await self.repo.update_ai_categorization(shipment_id, tenant_id, category, confidence, embedding)
        await self.db.commit()
        # print("✅ AI PROCESS COMPLETE")
