import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db
from main import app
from models.pacient_model import Pacient
from models.staff_model import Staff
from models.appointment_model import AppointmentStatus
from schemas.pacient_schema import PacientSchema, InactivatePacientSchema
from schemas.paciente_update_schema import PacientUpdateSchema
from schemas.appointment_schema import AppointmentCreate
from datetime import datetime, timedelta, timezone
from services.auth_service import get_current_user
from dotenv import load_dotenv
from sqlalchemy import text
from fastapi import Body
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_db_postgres():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pacient RESTART IDENTITY CASCADE"))
    yield

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


from services.auth_service import get_current_user

def fake_current_user():
    return {"username": "john doe", "role": "RECEPCIONISTA"}

app.dependency_overrides[get_current_user] = fake_current_user
client = TestClient(app)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def create_test_pacient(db, cpf="12345678901"):
    pacient = Pacient(
        id=5,
        full_name="Teste User",
        birth_date="01012000",
        cpf=cpf,
        hashed_password="fakehash",
        gender="Masculino",
        phone_number="11999999999",
        address="Rua Teste",
        email="test@example.com",
        blood_type="O+",
        known_allergies="None",
        role="PACIENT",
        is_active=True
    )
    db.add(pacient)
    db.commit()
    db.refresh(pacient)
    return pacient


def test_search_patient_by_id(db_session):
    p = create_test_pacient(db_session)
    response = client.get(f"/pacients/search-patient?id={p.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == p.id


@pytest.mark.parametrize("cpf", ["11122233381", "49572057207"])
def test_add_new_pacient(cpf):
    payload = {
        "full_name": "Novo Paciente",
        "birth_date": "01012000",
        "cpf": cpf,
        "hashed_password": "password",
        "gender": "Feminino",
        "phone_number": "11988887777",
        "address": "Rua Nova",
        "email": "",
        "blood_type": "A-",
        "known_allergies": ""
    }
    response = client.post("/pacients/add-new-pacient", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Usuário criado com sucesso."
    assert data["id"] > 0


def test_update_pacient_concurrent(db_session):
    p = create_test_pacient(db_session, cpf="22233344455")
    payload = {"full_name": "Alterado", "version_id": p.version_id - 1}
    response = client.patch(f"/pacients/update-pacient/{p.id}", json=payload)
    assert response.status_code == 409


def test_inactivate_patient(db_session):
    p = create_test_pacient(db_session, cpf="33344455566")
    payload = {"reason": "Motivo Teste"}
    response = client.post(f"/pacients/inactivate-patient/{p.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["pacient_id"] == p.id
    assert data["inactivated_by"]


def test_schedule_appointment(db_session):
    p = create_test_pacient(db_session, cpf="44455566677")
    from models.staff_model import Staff
    doctor = Staff(username="Dr. Teste", cpf="99988877766", hashed_password="hsuhd82731", role="DOCTOR")
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    payload = {
        "pacient_id": p.id,
        "doctor_id": doctor.id,
        "scheduled_at": (datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + timedelta(days=1)).isoformat()
    }
    response = client.post("/appointments/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["pacient_id"] == p.id
    assert data["doctor_id"] == doctor.id
    assert data["status"] == AppointmentStatus.SCHEDULED.value
