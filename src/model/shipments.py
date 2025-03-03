
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import BIGINT, FLOAT, VARCHAR, INTEGER, BOOLEAN, TIMESTAMP

from core.connection.postgres import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
    )
    time: Mapped[int] = mapped_column(INTEGER)
    weight_kg: Mapped[float] = mapped_column(FLOAT)
    volume_m3: Mapped[float] = mapped_column(FLOAT)
    eta_min: Mapped[int] = mapped_column(INTEGER)
    status: Mapped[str] = mapped_column(VARCHAR(255))
    forecast_origin_wind_velocity_mph: Mapped[float] = mapped_column(FLOAT)
    forecast_origin_wind_direction: Mapped[str] = mapped_column(VARCHAR(255))
    forecast_origin_precipitation_chance: Mapped[float] = mapped_column(FLOAT)
    forecast_origin_precipitation_kind: Mapped[str] = mapped_column(VARCHAR(255))
    origin_solar_system: Mapped[str] = mapped_column(VARCHAR(255))
    origin_planet: Mapped[str] = mapped_column(VARCHAR(255))
    origin_country: Mapped[str] = mapped_column(VARCHAR(255))
    origin_address: Mapped[str] = mapped_column(VARCHAR(255))
    destination_solar_system: Mapped[str] = mapped_column(VARCHAR(255))
    destination_planet: Mapped[str] = mapped_column(VARCHAR(255))
    destination_country: Mapped[str] = mapped_column(VARCHAR(255))
    destination_address: Mapped[str] = mapped_column(VARCHAR(255))
    
    created_at: Mapped[bool] = mapped_column(TIMESTAMP, default=func.now())
    is_deleted: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    deleted_at: Mapped[bool] = mapped_column(TIMESTAMP, nullable=True)
    is_restored: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    restored_at: Mapped[bool] = mapped_column(TIMESTAMP, nullable=True)