from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class PacientSchema(BaseModel):
    full_name: str = Field(min_length=5, max_length=100)
    birth_date: str = Field(min_length=8, max_length=8)
    cpf: str = Field(min_length=11, max_length=11)
    hashed_password: str = Field(min_length=6, max_length=30)
    gender: str = Field(min_length=3, max_length=10)
    phone_number: str = Field(min_length=11, max_length=11)
    address: str = Field(min_length=5, max_length=60)
    email: Optional[str] = None
    blood_type: Optional[str] = None
    known_allergies: Optional[str] = None

    @field_validator("email", mode="after")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v
    
class InactivatePacientSchema(BaseModel):
    reason: str = Field(min_length=1, max_length=200,
                        description="Motivo detalhado para inativação")