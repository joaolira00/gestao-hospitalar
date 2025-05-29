from passlib.context import CryptContext
from database.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from models.pacient_model import Pacient
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from models.staff_model import Staff
import os


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")


db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(cpf: str, password: str, db: db_dependency):
    staff = db.query(Staff).filter(Staff.cpf == cpf).first()
    if staff and bcrypt_context.verify(password, staff.hashed_password):
        return staff
    
    patient = db.query(Pacient).filter(Pacient.cpf == cpf).first()
    if patient and bcrypt_context.verify(password, patient.hashed_password):
        return patient
    
    return False


def create_access_token(cpf: str, role: str,
                        user_id: str, username: str,
                        expires_delta: timedelta):
    encode = {"sub": cpf, "id": user_id, "role": role, "username": username}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, secret_key, algorithm=algorithm)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        cpf: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        username: str = payload.get("username")

        if cpf is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")

        return {"cpf": cpf, "id": user_id, "role": role, "username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")