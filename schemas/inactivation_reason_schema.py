from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date

class InactivationReason(BaseModel):
    reason: str = Field(min_length=3, max_length=100)