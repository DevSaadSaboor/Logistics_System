from .repository import ShipmentRespository, StatusLogRepostiry
from app.modules.AI.categorizer import ShipmentCategorizer
from app.core.exceptions import (
    ShipmentNotFoundError,
    InvalidStatusTransitionError,
)
from app.core.logging import logger
from .enum import ShipmentStatus
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from datetime import timedelta,datetime
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
            raise ShipmentNotFoundError()
        current_status = shipment.status
        new_status.value if hasattr(new_status,"value") else new_status

        if current_status == new_status:
            logger.warning(
                "shipment.update_status.invalid no_op shipment_id=%s status=%s",
                shipment_id,
                current_status,
            )
            raise InvalidStatusTransitionError("Status is already set")
        allowed = self.ALLOWED_TRANSITIONS.get(current_status.value,[])
        if new_status not in allowed:
            logger.warning(
                "shipment.update_status.invalid_transition shipment_id=%s from=%s to=%s",
                shipment_id,
                current_status,
                new_status,
            )
            raise InvalidStatusTransitionError(f"Invalid status transition from {current_status} to {new_status}")
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

    
    def calculate_expected_delivery_date(self, pickup_date: datetime, weight: float, origin: str, destination: str) -> datetime:
        distance_km = 100.0  # Default fallback distance
        try:
            geolocator = Nominatim(user_agent="logistics_backend")
            loc_origin = geolocator.geocode(origin, timeout=3)
            loc_dest = geolocator.geocode(destination, timeout=3)
            if loc_origin and loc_dest:
                coords_1 = (loc_origin.latitude, loc_origin.longitude)
                coords_2 = (loc_dest.latitude, loc_dest.longitude)
                # great_circle is Geopy's implementation of the Haversine formula
                distance_km = great_circle(coords_1, coords_2).kilometers
        except Exception:
            pass
            
        # Base days: 1 day per 100 km
        days = max(1, int(distance_km / 400))
        
        # Add 1 extra day for every 50 weight units
        days += int(weight / 50)
        
        expected_delivery_date = pickup_date
        added_days = 0
        while added_days < days:
            expected_delivery_date += timedelta(days=1)
            # Skip weekends (5 is Saturday, 6 is Sunday)
            if expected_delivery_date.weekday() < 5:
                added_days += 1
                
        return expected_delivery_date

    async def create_shipment(self,tenant_id,origin,destination,weight,recipient_name,recipient_phone,delivery_address,pickup_date,description,assign_driver_id= None, user_id=None):
        expected_delivery_date = self.calculate_expected_delivery_date(pickup_date, weight, origin, destination)
        category = "other"
        confidence = 0.0
        tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        status =  ShipmentStatus.CREATED
        shipment = await self.repo.create_shipment(tenant_id,tracking_number,status,origin,destination,weight,recipient_name,recipient_phone,delivery_address,pickup_date,expected_delivery_date,description,category,confidence,assign_driver_id)
        await self.db.flush()
        await self.status_log.create_status_log(shipment.id,status,origin,user_id)
        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment

    async def run_ai_categorization(self, shipment_id: int, tenant_id, description: str):
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
        await self.status_log.create_status_log(shipment.id, status, shipment.origin, shipment.assign_driver_id)

        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment
    
    async def get_similar_shipment(self,shipment_id,tenant_id,min_similarity = 0.7,limit = 5,offset = 0):
        result =  await self.repo.get_similar_shipment(shipment_id,tenant_id,min_similarity,limit,offset)
        return [
            {
                "shipment": row[0],
                "similarity":round(1-float(row[1]),4)
            }
            for row in result   
        ]
    
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
            logger.warning(
                "shipment.track.not_found tracking_number=%s",
                tracking_number,
            )
            raise ShipmentNotFoundError()
        
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
        

    



        

    




