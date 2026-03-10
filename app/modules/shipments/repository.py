from .models import Shipments,Shipment_Staus_log
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update

class ShipmentRespository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_shipment(self,tenant_id, status,tracking_number,created_at,origin,destination,weight,recipient_name,recipient_phone,delivery_address,assign_driver_id = None):
        shipment = Shipments(tenant_id = tenant_id, 
                             tracking_number = tracking_number,
                             status = Shipment_Staus_log.status,
                             origin = origin, 
                             destination= destination,
                             weight = weight,
                             recipient_name = recipient_name,
                             recipient_phone = recipient_phone, 
                             delivery_address = delivery_address, 
                             assign_driver_id =assign_driver_id)
        self.db.add(shipment)
        return shipment

    async def get_by_tracking_number(self,tracking_number):
        result = await self.db.execute(select(Shipments).where(Shipments.tracking_number == tracking_number)) 
        return result.scalars().first()
    
    async def get_by_id(self,id):
        result = await self.db.execute(select(Shipments).where(Shipments.id == id))
        return result.scalars().first()
    

    async def update_status(self,status,shipment_id):
        result =(update(Shipments).where(Shipments.id == shipment_id).values(status = status))
        await self.db.execute(result)

    async def assign_driver(self,shipment_id,driver_id):
        result = (update(Shipments).where(Shipments.id == shipment_id).values( assign_driver_id = driver_id))
        await self.db.execute(result)
        
    

        
    

        