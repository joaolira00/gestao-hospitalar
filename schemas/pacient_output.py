from pydantic import BaseModel, EmailStr
from typing import Optional

class PacientOutput(BaseModel):
    id: int
    full_name: str
    birth_date: str
    cpf: str
    gender: str
    phone_number: str
    address: str
    email: Optional[str]
    blood_type: Optional[str]
    known_allergies: Optional[str]

    class Config:
        from_attributes = True
