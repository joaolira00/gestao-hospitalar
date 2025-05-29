from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date

class PacientUpdateSchema(BaseModel):
    full_name: Optional[str] = Field(None, min_length=5, max_length=100)
    birth_date: Optional[str]
    gender: Optional[str] = Field(None, min_length=3, max_length=10)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11)
    address: Optional[str] = Field(None, min_length=5, max_length=60)
    email: Optional[str]
    blood_type: Optional[str]
    known_allergies: Optional[str]
    version_id: int  = Field(description="Version control")