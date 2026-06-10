import asyncio
import logging
import os
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.modules.AI.categorizer import ShipmentCategorizer
from app.modules.shipments.repository import ShipmentRespository


class ShipmentAiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShipmentRespository(db)
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_embedding(self, text: str):
        if self.client is None:
            logger.warning("ai.embedding.skipped reason=no_openai_key")
            return None
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("ai.embedding.failed error=%s", e)
            return None

    async def categorizer_and_update_shipment(
        self,
        shipment_id: UUID,
        tenant_id: UUID,
        description: str,
    ):
        logger.info(
            "ai.categorization.started shipment_id=%s tenant_id=%s",
            shipment_id,
            tenant_id,
        )
        categorizer = ShipmentCategorizer()
        try:
            result = await asyncio.to_thread(categorizer.categorize, description)
            category = result.category
            confidence = result.confidence
            logger.info(
                "ai.categorization.result shipment_id=%s category=%s confidence=%s",
                shipment_id,
                category,
                confidence,
            )
        except Exception as e:
            logger.error("ai.categorization.failed shipment_id=%s error=%s", shipment_id, e)
            category = "other"
            confidence = 0.0

        # --- Generate embedding ---
        try:
            embedding = await self.generate_embedding(description)
        except Exception as e:
            logger.error("ai.embedding.error shipment_id=%s error=%s", shipment_id, e)
            embedding = None

        if AsyncSessionLocal is None:
            logger.error("ai.categorization.db_error reason=no_session_factory")
            return

        try:
            async with AsyncSessionLocal() as session:
                repo = ShipmentRespository(session)
                await repo.update_ai_categorization(
                    shipment_id, tenant_id, category, confidence, embedding
                )
                await session.commit()
                logger.info(
                    "ai.categorization.saved shipment_id=%s category=%s embedding=%s",
                    shipment_id,
                    category,
                    "yes" if embedding else "no",
                )
        except Exception as e:
            logger.error(
                "ai.categorization.db_write_failed shipment_id=%s error=%s",
                shipment_id,
                e,
            )
