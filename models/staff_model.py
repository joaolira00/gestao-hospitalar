from database.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Staff(Base):
    __tablename__ = "staff_member"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    appointments = relationship(
        "Appointment", back_populates="doctor", cascade="all, delete-orphan")