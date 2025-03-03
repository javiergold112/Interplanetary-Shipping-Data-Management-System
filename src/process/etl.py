from time import sleep
from typing import List, Set, Dict, Tuple
from config import AppConfig
from data import FetchDao, RedisDao, PostgreDAO
from data.dto.shipment import Shipment


class CosmoCargoProcess:
    def __init__(self):
        self.fetch_dao = FetchDao("https://censibal.github.io/txr-technical-hiring/")
        self.redis_dao = RedisDao()
        self.postgres_dao = PostgreDAO()

    def start(self):
        while True:
            if self.if_end():
                break
            sleep(AppConfig.FETCH_INTERVAL)
            self.do()

    def do(self):
        # get data from web source and database
        source_data: List[Shipment] = self.fetch_dao.get_data()
        existing_data: List[Shipment] = self.postgres_dao.get_all()

        # determine data to delete, insert, update
        restore_data: List[Shipment] = self.get_restore_shipments(source_data, existing_data)
        delete_data: List[Shipment] = self.get_del_shipments(source_data, existing_data)
        new_shipments: List[Shipment] = self.get_new_shipments(source_data, existing_data)
        
        print(f"len restore_data = {len(restore_data)}")
        print(f"len delete_data = {len(delete_data)}")
        print(f"len new_shipments = {len(new_shipments)}")
        
        # update db
        self.postgres_dao.bulk_insert(new_shipments)
        self.postgres_dao.bulk_delete_by_ids([shipment.id for shipment in delete_data])
        self.postgres_dao.bulk_restore_by_ids([shipment.id for shipment in restore_data])


    def get_new_shipments(self, source_data:List[Shipment], existing_data:List[Shipment]) -> List[Shipment]:
        existing_shipment_keys: Set[str] = set()
        for shipment in existing_data:
            if not shipment.is_deleted:
                key = self._create_shipment_key(shipment)
                existing_shipment_keys.add(key)
        
        new_shipments: List[Shipment] = []
        for shipment in source_data:
            key = self._create_shipment_key(shipment)
            if key not in existing_shipment_keys:
                new_shipments.append(shipment)
        
        return new_shipments


    def get_del_shipments(self, source_data:List[Shipment], existing_data:List[Shipment]) -> List[Shipment]:
        new_shipment_keys: Set[str] = set()
        for shipment in source_data:
            key = self._create_shipment_key(shipment)
            new_shipment_keys.add(key)
        
        delete_shipments: List[Shipment] = []
        for shipment in existing_data:
            if not shipment.is_deleted:
                key = self._create_shipment_key(shipment)
                if key not in new_shipment_keys:
                    delete_shipments.append(shipment)
        
        return delete_shipments

    
    def get_restore_shipments(self, source_data:List[Shipment], existing_data:List[Shipment]) -> List[Shipment]:
        new_shipment_keys: Set[str] = set()
        for shipment in source_data:
            key = self._create_shipment_key(shipment)
            new_shipment_keys.add(key)
        
        restore_shipments: List[Shipment] = []
        for shipment in existing_data:
            if shipment.is_deleted:
                key = self._create_shipment_key(shipment)
                if key in new_shipment_keys:
                    restore_shipments.append(shipment)
        
        return restore_shipments


    def _create_shipment_key(self, shipment: Shipment) -> str:
        fields = [
            "time",
            "weight_kg",
            "volume_m3",
            "eta_min",
            "status",
            "forecast_origin_wind_velocity_mph",
            "forecast_origin_wind_direction",
            "forecast_origin_precipitation_chance",
            "forecast_origin_precipitation_kind",
            "origin_solar_system",
            "origin_planet",
            "origin_country",
            "origin_address",
            "destination_solar_system",
            "destination_planet",
            "destination_country",
            "destination_address",
        ]
        
        return ",".join([str(getattr(shipment, f)) for f in fields])

    def if_end(self):
        return False