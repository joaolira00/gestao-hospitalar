from pydantic import BaseModel, Field
from typing import Optional

class UpdatePacient(BaseModel):
    full_name: str = Field(min_length=5, max_length=100)
    birth_date: str = Field(min_length=8, max_length=8)
    phone_number: str = Field(min_length=11, max_length=11)
    address: str = Field(min_length=5, max_length=60)
    email: Optional[str] = None
    version_id: int  = Field(description="Version control")