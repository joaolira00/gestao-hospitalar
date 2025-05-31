from pydantic import BaseModel, Field

class InactivationReason(BaseModel):
    reason: str = Field(min_length=3, max_length=100)