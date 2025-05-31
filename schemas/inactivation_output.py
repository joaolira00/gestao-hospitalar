from pydantic import BaseModel

class InactivationOut(BaseModel):
    pacient_id: int
    was_active: bool
    inactivated_at: str
    inactivated_by: str
    reason: str
