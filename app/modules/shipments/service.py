from .repository import ShipmentRespository, StatusLogRepostiry
from app.modules.AI.categorizer import ShipmentCategorizer
from fastapi import HTTPException
from .enum import ShipmentStatus
import uuid

class ShipmentsService():
    def __init__(self,db):
        self.db = db
        self.repo = ShipmentRespository(db)
        self.status_log = StatusLogRepostiry(db)
    
    ALLOWED_TRANSITIONS = {
    "CREATED": ["ASSIGNED"],
    "ASSIGNED": ["PICKED_UP"],
    "PICKED_UP": ["IN_TRANSIT"],
    "IN_TRANSIT": ["DELIVERED"],
    "DELIVERED": []
    }
    async def update_status(self,shipment_id,tenant_id,new_status,user_id):
        shipment  = await self.repo.get_by_id_for_update(shipment_id,tenant_id)
        if not shipment:
            raise HTTPException(status_code= 404, detail="shipment not found")
        current_status = shipment.status
        current_status_value = current_status.value
        new_status_value = new_status.value if hasattr(new_status,"value") else new_status

        if current_status == new_status:
            raise HTTPException(status_code=400 , detail="status already set")
        allowed = self.ALLOWED_TRANSITIONS.get(current_status.value,[])
        if new_status not in allowed:
            raise HTTPException(status_code=400 ,detail=f"Invalid transition from {current_status} to {new_status}")
        shipment.status = new_status

        await self.db.flush()
        await self.status_log.create_status_log(
            shipment.id,
            new_status,
            shipment.destination,
            user_id
        )
        await self.db.commit()
        return shipment



    
    async def create_shipment(self,tenant_id,origin,destination,weight,recipient_name,recipient_phone,delivery_address,pickup_date,delivery_date,description,assign_driver_id= None, user_id=None):
        category = "other"
        confidence = 0.0
        tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        status =  ShipmentStatus.CREATED
        shipment = await self.repo.create_shipment(tenant_id,tracking_number,status,origin,destination,weight,recipient_name,recipient_phone,delivery_address,pickup_date,delivery_date,description,category,confidence,assign_driver_id)
        await self.db.flush()
        status_log = await self.status_log.create_status_log(shipment.id,status,origin,user_id)
        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment

    async def run_ai_categorization(self , shipment_id:int , description:str):
        categorizer = ShipmentCategorizer()
        try:
            result = categorizer.categorize(description)
            category = result.category
            confidence = result.confidence
        except Exception:
            category = "other"
            confidence = 0.0
        await self.repo.update_ai_fields(
            shipment_id,
            category,
            confidence
        )
        await self.db.commit()
    

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
        if not shipment:
            raise HTTPException(status_code= 404, detail="shipment not found")
        
        logs = await self.status_log.get_logs_by_shipment_id(shipment.id)

        phone = shipment.recipient_phone
        masked_phone  = f"****{phone[-4:]}" if phone else None

        return {
            "tracking_number": shipment.tracking_number,
            "status" : shipment.status,
            "origin": shipment.origin,
            "destination" : shipment.destination,
            "recipient_name": shipment.recipient_name,
            "recipient_phone": masked_phone,
            "history" : [
                {
                    "status" : log.status,
                    "location":log.location,
                    "timestamp": log.timestamp
                }
                for log in logs
            ]
        }
        

    



        

    




