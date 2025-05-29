from fastapi import APIRouter, Depends, HTTPException
from schemas.pacient_schema import PacientSchema
from models.pacient_model import Pacient
from starlette import status
from database.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service import (
    authenticate_user, bcrypt_context, create_access_token
)
from datetime import timedelta
from models.token_model import Token
from services.auth_service import get_current_user
from schemas.staff_schema import StaffSchema
from models.staff_model import Staff


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all-user", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    users_model = db.query(Staff).all()
    if users_model is None or len(users_model) < 1:
        raise HTTPException(status_code=404, detail="Users not found")
    else:
        return users_model


@router.post("/create-new-staff-member",
             status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_staff_request: StaffSchema):
    create_user_model = Staff(
        cpf=create_staff_request.cpf,
        username=create_staff_request.username,
        hashed_password=bcrypt_context.hash(create_staff_request
                                            .hashed_password),
        role=create_staff_request.role
    )

    db.add(create_user_model)
    db.commit()



@router.post("/login", response_model=Token)
async def login_for_access_token(form_data:
                                 Annotated[OAuth2PasswordRequestForm,
                                           Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")
    token = create_access_token(cpf=user.cpf,
                                user_id=user.id,
                                role=user.role,
                                username=user.username,
                                expires_delta=timedelta(minutes=30))

    return {"access_token": token, "token_type": "bearer"}