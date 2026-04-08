from .models import Shipments,Shipment_Staus_log
from sqlalchemy.ext.asyncio import AsyncSession
from .enum import ShipmentStatus
from sqlalchemy import select,update
from sqlalchemy.sql import func

class ShipmentRespository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_shipment(self, tenant_id, tracking_number, status, origin, destination,weight, recipient_name, recipient_phone, 
                              delivery_address,pickup_date, delivery_date, description, category, confidence,assign_driver_id=None):
        shipment = Shipments(
            tenant_id=tenant_id,
            tracking_number=tracking_number,
            status=status.value if hasattr(status, "value") else status,
            origin=origin,
            destination=destination,
            weight=weight,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            delivery_address=delivery_address,
            pickup_date=pickup_date,
            delivery_date=delivery_date,
            description=description,
            category=category,
            confidence=confidence,
            assign_driver_id=assign_driver_id
        )
        self.db.add(shipment)
        return shipment

    async def update_ai_fields(self, shipment_id, category, confidence):
        stmt = (
            update(Shipments)
            .where(Shipments.id == shipment_id) 
            .values(category=category, confidence=confidence, ai_processed=True, ai_processed_at=func.now())
        )
        await self.db.execute(stmt)

    async def update_ai_categorization(self, shipment_id, tenant_id, category, confidence):
        stmt = (
            update(Shipments)
            .where(Shipments.id == shipment_id, Shipments.tenant_id == tenant_id)
            .values(category=category, confidence=confidence, ai_processed=True, ai_processed_at=func.now())
        )
        await self.db.execute(stmt)

    async def get_by_tracking_number(self, tracking_number):
        result = await self.db.execute(select(Shipments).where(Shipments.tracking_number == tracking_number))
        return result.scalars().first()

    async def get_by_id(self, id):
        result = await self.db.execute(select(Shipments).where(Shipments.id == id))
        return result.scalars().first()

    async def update_status(self, shipment_id, status):
        result = (update(Shipments).where(Shipments.id == shipment_id).values(status=status))
        await self.db.execute(result)

    async def assign_driver(self, shipment_id, driver_id):
        result = (update(Shipments).where(Shipments.id == shipment_id).values(assign_driver_id=driver_id))
        await self.db.execute(result)

    
    async def get_by_id_for_update(self,shipment_id,tenant_id):
        result = await self.db.execute (select(Shipments).where(Shipments.id == shipment_id)
        .where(Shipments.tenant_id == tenant_id).with_for_update())

        return result.scalars().first()


class StatusLogRepostiry:
    def __init__(self,db:AsyncSession):
        self.db = db
    
    async def create_status_log(self,shipment_id,status,location, user_id):
       log = Shipment_Staus_log(
           shipment_id = shipment_id,
           updated_by_user_id= user_id,
           status=status.value if hasattr(status, "value") else status,
           location = location
       )
       self.db.add(log)
       return log
    
    async def get_logs_by_shipment_id(self,shipment_id):
        result = await self.db.execute(select(Shipment_Staus_log).where(Shipment_Staus_log.shipment_id == shipment_id)
        .order_by(Shipment_Staus_log.timestamp.asc()))
        return result.scalars().all()
    


    



       
        
    

        
    

        