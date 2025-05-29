from database.database import Base
from sqlalchemy import Column, Integer, String, text, Boolean
from sqlalchemy.orm import relationship

class Pacient(Base):
    __tablename__ = "pacient"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    birth_date = Column(String)
    cpf = Column(String, unique=True)
    hashed_password = Column(String)
    gender = Column(String)
    phone_number = Column(String)
    address = Column(String)
    email = Column(String, nullable=True)
    blood_type = Column(String, nullable=True)
    known_allergies = Column(String, nullable=True)
    role = Column(String, nullable=False, default="PACIENT", server_default=text("'PACIENT'"))
    version_id = Column(Integer, nullable=False, default=1)
    history = relationship("PacientHistory", back_populates="pacient")
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    inactivations  = relationship("PacientInactivation", back_populates="pacient",
                                  cascade="all, delete-orphan")
    appointments = relationship(
        "Appointment", back_populates="pacient", cascade="all, delete-orphan")
