from sqlalchemy.orm.session import Session
from datetime import datetime
from data.dto.shipment import Shipment as ShipmentDTO
from utils import init_session
from model.shipments import Shipment as ShipmentModel
from sqlalchemy import select, delete, insert, update


class PostgreDAO:
    def __init__(self):
        self.model = ShipmentModel
    
    @init_session
    def bulk_insert(self, db: Session, shipments: list[ShipmentDTO] = []):
        if not shipments:
            return
            
        # Convert DTOs to dictionaries that can be used with SQLAlchemy
        shipment_dicts = [shipment.model_dump() for shipment in shipments]
        
        for shipment in shipment_dicts:
            del shipment['id']
            del shipment['is_deleted']
        # created_at is handled by default value in the model
        
        # Use SQLAlchemy's insert statement for bulk insertion
        stmt = insert(self.model).values(shipment_dicts)
        
        # Execute the insert statement
        db.execute(stmt)
        db.commit()

    @init_session
    def bulk_delete_by_ids(self, db: Session, ids: list[int] = []):
        if not ids:
            return
            
        # Update the is_deleted field to True and set deleted_at timestamp
        stmt = update(self.model).where(
            self.model.id.in_(ids)
        ).values(
            is_deleted=True,
            deleted_at=datetime.now()
        )
        
        db.execute(stmt)
        db.commit()

    @init_session
    def bulk_restore_by_ids(self, db: Session, ids: list[int] = []):
        if not ids:
            return
            
        # Update to restore the shipments
        stmt = update(self.model).where(
            self.model.id.in_(ids)
        ).values(
            is_deleted=False,
            is_restored=True,
            restored_at=datetime.now()
        )
        
        db.execute(stmt)
        db.commit()

    @init_session
    def get_all(self, db: Session):
        query = select(self.model).where(self.model.is_deleted == False)
        return db.execute(query).scalars().all()