from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date

class UpdatePacient(BaseModel):
    full_name: str = Field(min_length=5, max_length=100)
    version_id: int  = Field(description="Version control")