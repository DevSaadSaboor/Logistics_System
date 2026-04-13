import asyncio
from app.modules.AI.categorizer import ShipmentCategorizer
from app.modules.shipments.repository import ShipmentRespository
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ShipmentAiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShipmentRespository(db)
        api_key = os.getenv("OPENAI_API_KEY")   
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_embedding(self, text: str):
        try:
            response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print("❌ EMBEDDING ERROR:", e)
            return None

    async def categorizer_and_update_shipment(self, shipment_id: UUID, tenant_id, description: str):

        print("AI SERVICE TRIGGERED")
        categorizer = ShipmentCategorizer()
        try:
            print("➡️ Running categorizer...")
            result = await asyncio.to_thread(categorizer.categorize, description)
            category = result.category
            confidence = result.confidence
            print("➡️ Generating embedding...")
            embedding = self.generate_embedding(description)
            print("Embedding:", type(embedding), len(embedding) if embedding else "None")
            print("✅ Embedding length:", len(embedding))
        except Exception as e :
            print("❌ AI ERROR:", e)
            category = "other"
            confidence = 0.0
            embedding = None
            print("➡️ Saving to DB...")

        await self.repo.update_ai_categorization(shipment_id, tenant_id, category, confidence, embedding)
        await self.db.commit()
        print("✅ AI PROCESS COMPLETE")
