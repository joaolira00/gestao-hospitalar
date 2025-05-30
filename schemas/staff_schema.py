from pydantic import BaseModel, Field


class StaffSchema(BaseModel):
    username: str = Field(min_length=5, max_length=100)
    hashed_password: str = Field(min_length=6, max_length=30)
    cpf: str = Field(min_length=11, max_length=11)
    role: str = Field(min_length=3, max_length=15)