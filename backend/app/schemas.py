from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TripPoint(BaseModel):
    lon: float
    lat: float
    t: float | None = None
    speed_kph: float | None = None


class TripSummary(BaseModel):
    trip_id: int
    log_date: date
    devid: int | None = None
    distance_km: float | None = None
    duration_seconds: float | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    avg_speed_kph: float | None = None


class TripDetail(TripSummary):
    points: list[TripPoint] = Field(default_factory=list)


class Segment(BaseModel):
    start: tuple[float, float]  # (lon, lat)
    end: tuple[float, float]
    speed_kph: float | None = None
    status: Literal["congested", "smooth"]


class TripSegmentsResponse(BaseModel):
    trip: TripSummary
    congestion_threshold_kph: float
    segments: list[Segment]


class CarProfile(BaseModel):
    device_id: str
    total_distance: float
    trips_total: int
    trip_ids: list[int] = Field(default_factory=list)
    trips_distance: list[float] = Field(default_factory=list)

    trips_total_by_2h: dict[str, int] = Field(default_factory=dict)
    total_distance_by_2h: dict[str, float] = Field(default_factory=dict)


class CarTripsItem(BaseModel):
    trip_id: int
    log_date: date
    distance_km: float | None = None
    duration_seconds: float | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class HealthResponse(BaseModel):
    ok: bool = True
    db: Literal["up", "down"] = "up"
    details: dict[str, Any] = Field(default_factory=dict)

