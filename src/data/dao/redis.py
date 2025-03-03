from typing import List, Optional
import uuid
from core.connection.redis import redis_con
from data.dto.shipment import Shipment


class RedisDao:
    def __init__(self):
        self.redis = redis_con
        self.shipment_key_prefix = "shipment:"
        self.shipment_index_key = "shipment:all"
    
    def get_shipment_key(self, shipment_id: str) -> str:
        """Generate a Redis key for a specific shipment"""
        return f"{self.shipment_key_prefix}{shipment_id}"
    
    def insert_shipment(self, shipment: Shipment, shipment_id: str = None) -> str:
        """
        Insert a shipment into Redis
        
        Args:
            shipment: The Shipment object to insert
            shipment_id: Optional custom ID. If not provided, will use timestamp + random suffix
            
        Returns:
            The ID of the inserted shipment
        """
        if shipment_id is None:
            # Create a unique ID based on timestamp and a random suffix
            shipment_id = f"{shipment.time}_{uuid.uuid4().hex[:8]}"
        
        # Convert shipment to JSON
        shipment_json = shipment.model_dump_json()
        
        # Insert into Redis
        shipment_key = self.get_shipment_key(shipment_id)
        
        # Use a pipeline for atomicity
        pipe = self.redis.pipeline()
        pipe.set(shipment_key, shipment_json)
        pipe.sadd(self.shipment_index_key, shipment_id)  # Add to index set
        pipe.execute()
        
        return shipment_id
    
    def insert_shipments(self, shipments: List[Shipment]) -> List[str]:
        """
        Insert multiple shipments into Redis
        
        Args:
            shipments: List of Shipment objects to insert
            
        Returns:
            List of IDs of the inserted shipments
        """
        shipment_ids = []
        
        # Use a pipeline for better performance
        pipe = self.redis.pipeline()
        
        for shipment in shipments:
            # Create a unique ID for each shipment
            shipment_id = f"{shipment.time}_{uuid.uuid4().hex[:8]}"
            shipment_ids.append(shipment_id)
            
            # Convert shipment to JSON
            shipment_json = shipment.model_dump_json()
            
            # Add commands to pipeline
            shipment_key = self.get_shipment_key(shipment_id)
            pipe.set(shipment_key, shipment_json)
            pipe.sadd(self.shipment_index_key, shipment_id)
        
        # Execute all commands in a single round-trip
        pipe.execute()
        
        return shipment_ids
    
    def get_shipment(self, shipment_id: str) -> Optional[Shipment]:
        """
        Get a shipment from Redis by ID
        
        Args:
            shipment_id: The ID of the shipment to retrieve
            
        Returns:
            The Shipment object if found, None otherwise
        """
        shipment_key = self.get_shipment_key(shipment_id)
        shipment_json = self.redis.get(shipment_key)
        
        if not shipment_json:
            return None
        
        # Convert JSON string to Shipment object
        return Shipment.model_validate_json(shipment_json)
    
    def get_all_shipments(self) -> List[Shipment]:
        """
        Get all shipments from Redis
        
        Returns:
            List of all Shipment objects
        """
        # Get all shipment IDs
        shipment_ids = self.redis.smembers(self.shipment_index_key)
        
        if not shipment_ids:
            return []
        
        # Use a pipeline for better performance
        pipe = self.redis.pipeline()
        
        # Add get commands to pipeline
        for shipment_id in shipment_ids:
            shipment_key = self.get_shipment_key(shipment_id.decode('utf-8') if isinstance(shipment_id, bytes) else shipment_id)
            pipe.get(shipment_key)
        
        # Execute all get commands
        shipment_jsons = pipe.execute()
        
        # Convert JSON strings to Shipment objects
        shipments = []
        for shipment_json in shipment_jsons:
            if shipment_json:
                shipments.append(Shipment.model_validate_json(shipment_json))
        
        return shipments
