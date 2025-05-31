from sqlalchemy import (
    Column, Integer, DateTime, Enum, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "Agendada"
    CANCELLED = "Cancelada"
    COMPLETED = "Realizada"

class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = (
        UniqueConstraint("doctor_id", "scheduled_at", name="uq_doctor_schedule"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pacient_id = Column(Integer, ForeignKey("pacient.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("staff_member.id"),   nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED,
                             nullable=False)

    pacient = relationship("Pacient", back_populates="appointments")
    doctor = relationship("Staff",   back_populates="appointments")
