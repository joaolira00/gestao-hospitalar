from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from database.database import Base

class PacientHistory(Base):
    __tablename__ = "pacient_history"

    id = Column(Integer, primary_key=True, index=True)
    pacient_id = Column(Integer, ForeignKey("pacient.id"), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)
    changed_by = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    pacient = relationship("Pacient", back_populates="history")