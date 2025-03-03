from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime


class Shipment(BaseModel):
    id: int|None = None
    time: int = Field(..., alias="time")
    weight_kg: float = Field(..., alias="weightKg")
    volume_m3: float = Field(..., alias="volumeM3")
    eta_min: int = Field(..., alias="etaMin")
    status: str = Field(..., alias="status")
    forecast_origin_wind_velocity_mph: float = Field(..., alias="forecastOriginWindVelocityMph")
    forecast_origin_wind_direction: str = Field(..., alias="forecastOriginWindDirection")
    forecast_origin_precipitation_chance: float = Field(..., alias="forecastOriginPrecipitationChance")
    forecast_origin_precipitation_kind: str = Field(..., alias="forecastOriginPrecipitationKind")
    origin_solar_system: str = Field(..., alias="originSolarSystem")
    origin_planet: str = Field(..., alias="originPlanet")
    origin_country: str = Field(..., alias="originCountry")
    origin_address: str = Field(..., alias="originAddress")
    destination_solar_system: str = Field(..., alias="destinationSolarSystem")
    destination_planet: str = Field(..., alias="destinationPlanet")
    destination_country: str = Field(..., alias="destinationCountry")
    destination_address: str = Field(..., alias="destinationAddress")
    
    is_deleted: bool|None = None
    deleted_at: datetime|None = None
    
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

        
    def get_timestamp_as_datetime(self) -> datetime:
        """Convert the timestamp to a datetime object"""
        return datetime.fromtimestamp(self.time)