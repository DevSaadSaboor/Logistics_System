from app.modules.AI.categorizer import ShipmentCategorizer
from app.modules.shipments.repository import ShipmentRespository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

class ShipmentAiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShipmentRespository(db)

    
    async def categorizer_and_update_shipment(self,shipment_id:int,tenant_id:int,description:str):
        categorizer = ShipmentCategorizer()
        try:
            result = categorizer.categorize(description)
            category = result.category
            confidence = result.confidence
        except Exception:
            category = "other"
            confidence= 0.0
        
        await self.repo.update_ai_categorization(shipment_id,tenant_id,category,confidence)

        await self.db.commit()
    



