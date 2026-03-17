from .models import Shipments, Shipment_Staus_log
from .repository import ShipmentRespository,StatusLogRepostiry
from datetime import datetime,timezone,timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from .enum import ShipmentStatus
from .enum import ShipmentStatus
import uuid

class ShipmentsService():
    def __init__(self,db):
        self.db = db
        self.repo = ShipmentRespository(db)
        self.status_log = StatusLogRepostiry(db)
    
    async def create_shipment(self,tenant_id,origin,destination,weight,recipient_name,recipient_phone,delivery_address,assign_driver_id= None, user_id=None):
        tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        status =  ShipmentStatus.CREATED
        shipment = await self.repo.create_shipment(tenant_id,tracking_number,status,origin,destination,weight,recipient_name,recipient_phone,delivery_address,assign_driver_id)
        await self.db.flush()
        status_log = await self.status_log.create_status_log(shipment.id,status,origin,user_id)

        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment
    

    async def update_shipment(self,shipment_id, status):
        shipment = await self.repo.get_by_id(shipment_id)
        await self.repo.update_status(shipment.id, status)
        status_log = await self.status_log.create_status_log(shipment.id, status, shipment.origin, shipment.assign_driver_id)

        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment
    
    async def assing_driver(self,shipment_id, status,driver_id , user_id):
        shipment = await self.repo.get_by_id(shipment_id)
        await self.repo.assign_driver(shipment.id, driver_id)
        await self.repo.update_status(shipment.id, ShipmentStatus.ASSIGNED.value)
        await self.status_log.create_status_log(shipment.id, ShipmentStatus.ASSIGNED.value,shipment.origin,user_id)
        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment
    
    async def get_by_tracking_number(self,tracking_number):
        shipment = await self.repo.get_by_tracking_number(tracking_number)
        return shipment

    



        

    




