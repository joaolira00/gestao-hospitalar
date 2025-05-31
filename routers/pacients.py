from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Response, Query, Body
from fastapi.responses import JSONResponse
from models.pacient_model import Pacient
from database.database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from services.auth_service import get_current_user
from services.auth_service import bcrypt_context
from schemas.pacient_schema import PacientSchema
from schemas.pacient_output import PacientOutput
from models.pacient_history_model import PacientHistory
from models.pacient_inactivation_model import PacientInactivation
from models.appointment_model import Appointment
from models.appointment_model import AppointmentStatus
from schemas.update_pacient_schema import UpdatePacient
from schemas.inactivation_reason_schema import InactivationReason

router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/search-patient", response_model=List[PacientOutput],
            status_code=status.HTTP_200_OK,
            summary="Buscar pacientes por ID, CPF ou nome")
def search_pacients(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    id: Optional[int] = Query(None, gt=0, description="Id do paciente"),
    cpf: Optional[str] = Query(None, min_length=11, max_length=14, description="CPF com ou sem formatação"),
    name: Optional[str] = Query(None, min_length=3, description="Parte ou nome completo do paciente"),
):
    
    if current_user.get("role") not in ("RECEPCIONISTA", "DOCTOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para acessar este método."
    )

    query = db.query(Pacient)


    if id is not None:
        query = query.filter(Pacient.id == id)
    if cpf is not None:
        from re import sub
        raw_cpf = sub(r"\D", "", cpf)
        query = query.filter(Pacient.cpf == raw_cpf)
    if name is not None:
        query = query.filter(Pacient.full_name.ilike(f"%{name}%"))

    results = query.all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum paciente encontrado."
        )

    return results


@router.post("/add-new-patient",
             status_code=status.HTTP_201_CREATED,
             response_model=None,
             summary="Cria um novo paciente")
async def add_pacient(db: db_dependency, 
                      create_pacient_request: PacientSchema, current_user: dict = Depends(get_current_user)):

    if current_user.get("role") != "RECEPCIONISTA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para acessar este método."
    )


    existing = (
        db.query(Pacient)
          .filter(Pacient.cpf == create_pacient_request.cpf)
          .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado."
        )

    pacient = Pacient(
        full_name=create_pacient_request.full_name,
        birth_date=create_pacient_request.birth_date,
        cpf=create_pacient_request.cpf,
        hashed_password=bcrypt_context.hash(create_pacient_request.hashed_password),
        gender=create_pacient_request.gender,
        phone_number=create_pacient_request.phone_number,
        address=create_pacient_request.address,
        email=create_pacient_request.email,
        blood_type=create_pacient_request.blood_type,
        known_allergies=create_pacient_request.known_allergies
    )

    db.add(pacient)
    db.commit()
    db.refresh(pacient)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Usuário criado com sucesso."}
    )


@router.patch(
    "/update-patient/{pacient_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualiza dados cadastrais de um paciente."  
)
def update_pacient(
    *,
    pacient_id: int = Path(..., gt=0),
    payload: UpdatePacient,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "RECEPCIONISTA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para acessar este método."
        )

    pacient = db.get(Pacient, pacient_id)
    if not pacient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado."
        )

    if payload["version_id"] != pacient.version_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dados desatualizados: atualize a tela e tente novamente"
        )

    data = payload.copy()
    data.pop("version_id", None)
    for field, new_value in data.items():
        old_value = getattr(pacient, field)
        if new_value != old_value:
            hist = PacientHistory(
                pacient_id=pacient.id,
                field_name=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value),
                changed_by=current_user.get("username")
            )
            db.add(hist)
            setattr(pacient, field, new_value)

    pacient.version_id += 1
    db.commit()
    db.refresh(pacient)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Usuário atualizado com sucesso."}
    )


@router.post(
    "/inactivate-patient/{pacient_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Inativa logicamente um cadastro de paciente"
)
def inactivate_pacient(
    *,
    pacient_id: int = Path(..., gt=0),
    payload: InactivationReason,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ("RECEPCIONISTA", "ADM"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente."
        )

    pacient = db.get(Pacient, pacient_id)
    if not pacient or not pacient.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado ou já inativo."
        )

    pendente = (
        db.query(Appointment)
          .filter(
             Appointment.pacient_id == pacient_id,
             Appointment.status == AppointmentStatus.SCHEDULED
          )
          .first()
    )
    if pendente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paciente possui consultas pendentes. Cancele-as antes de inativar."
        )

    pacient.is_active = False
    hist = PacientInactivation(
        pacient_id=pacient.id,
        reason=payload["reason"],
        inactivated_by=current_user.get("username")
    )
    db.add(hist)
    db.commit()
    db.refresh(hist)

    return {
        "pacient_id": pacient.id,
        "was_active": True,
        "inactivated_at": hist.inactivated_at.isoformat(),
        "inactivated_by": hist.inactivated_by,
        "reason": hist.reason
    }



@router.delete("/delete-patient/{pacient_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Deleta um paciente pelo ID")
async def delete_pacient(db: db_dependency, pacient_id: int = Path(gt=0)):
    
    pacient = db.query(Pacient).get(pacient_id)
    
    if not pacient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado."
        )

    db.delete(pacient)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)