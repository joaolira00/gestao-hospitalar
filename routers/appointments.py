from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from database.database import get_db
from models.appointment_model import Appointment, AppointmentStatus
from models.pacient_model import Pacient
from models.staff_model import Staff
from schemas.appointment_schema import AppointmentCreate, AppointmentOut
from services.auth_service import get_current_user
from typing import Annotated
from database.database import SessionLocal

router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post(
    "/",
    response_model=AppointmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agendar nova consulta médica"
)
def schedule_appointment(
    payload: AppointmentCreate,
    current_user: user_dependency,
    db: Session = Depends(get_db)):
    if current_user.get("role") != "RECEPCIONISTA":
        print(current_user.get("role"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente."
        )

    pacient = db.query(Pacient).get(payload.pacient_id)
    if not pacient or not getattr(pacient, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado ou inativo."
        )

    doctor = db.query(Staff).get(payload.doctor_id)
    if not doctor or doctor.role.upper() != "DOCTOR":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado."
        )

    appt = Appointment(
        pacient_id = payload.pacient_id,
        doctor_id = payload.doctor_id,
        scheduled_at = payload.scheduled_at,
        status = AppointmentStatus.SCHEDULED
    )
    db.add(appt)
    try:
        db.commit()
        db.refresh(appt)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horário já agendado para este médico."
        )

    return appt
