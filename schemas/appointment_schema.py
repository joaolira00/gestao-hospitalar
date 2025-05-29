from pydantic import BaseModel, Field, validator
from datetime import datetime, time
from typing import Optional

class AppointmentCreate(BaseModel):
    pacient_id: int = Field(..., gt=0)
    doctor_id:  int = Field(..., gt=0)
    scheduled_at: datetime = Field(..., description="Data e hora da consulta (UTC)")

    @validator("scheduled_at")
    def must_be_future(cls, v: datetime):
        if v <= datetime.utcnow():
            raise ValueError("Data/hora deve ser futura")
        local_time = v.time()
        if not time(8, 0) <= local_time <= time(17, 0):
            raise ValueError("Fora do horário de atendimento (08:00-17:00)")
        return v

class AppointmentOut(BaseModel):
    id: int
    pacient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: str

