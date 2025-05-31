from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional

class AppointmentCreate(BaseModel):
    pacient_id: int = Field(..., gt=0)
    doctor_id:  int = Field(..., gt=0)
    scheduled_at: datetime = Field(..., description="Data e hora da consulta (UTC)")

    @validator("scheduled_at")
    def check_future(cls, v: datetime) -> datetime:
        agora_utc = datetime.now(timezone.utc)
        if v <= agora_utc:
            raise ValueError("scheduled_at deve ser uma data futura")
        return v

class AppointmentOut(BaseModel):
    id: int
    pacient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: str