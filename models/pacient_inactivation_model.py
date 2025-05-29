from sqlalchemy import (
    Column, Integer, ForeignKey, String, DateTime, func
)
from sqlalchemy.orm import relationship
from database.database import Base

class PacientInactivation(Base):
    __tablename__ = "pacient_inactivation"

    id = Column(Integer, primary_key=True, index=True)
    pacient_id = Column(Integer, ForeignKey("pacient.id"), nullable=False)
    reason = Column(String, nullable=False)
    inactivated_by = Column(String, nullable=False)
    inactivated_at = Column(DateTime(timezone=True), server_default=func.now())
    pacient = relationship("Pacient", back_populates="inactivations")
