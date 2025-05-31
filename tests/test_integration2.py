import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.auth_service import get_current_user
from database.database import Base, get_db
from main import app
from models.pacient_model import Pacient
from models.appointment_model import AppointmentStatus
from datetime import datetime, timedelta, timezone
from models.staff_model import Staff

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_current_user():
    return {
        "username": "recep_teste",
        "role": "RECEPCIONISTA"
    }


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


def create_test_pacient(db, cpf="12345678901"):
    pacient = Pacient(
        id=5,
        full_name="Teste User",
        birth_date="20000101",
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


def test_search_pacient_success(client: TestClient, db_session):
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "recep_teste",
        "role": "RECEPCIONISTA"
    }

    pacient = create_test_pacient(db_session, cpf="12345678901")

    response = client.get(f"/patients/search-patient/?id={pacient.id}")
    assert response.status_code == 200

    


def test_schedule_appointment(db_session, client):
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "recep_teste",
        "role": "RECEPCIONISTA"
    }

    p = create_test_pacient(db_session, cpf="44455566677")
    doctor = Staff(username="Dr. Teste", cpf="99988877766", hashed_password="hsuhd82731", role="DOCTOR")
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    scheduled = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    payload = {
        "pacient_id": p.id,
        "doctor_id": doctor.id,
        "scheduled_at": scheduled,
        "status": "Agendada"
    }
    response = client.post("/appointments/schedule-appointment", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["pacient_id"] == p.id
    assert data["doctor_id"] == doctor.id
    assert data["status"] == AppointmentStatus.SCHEDULED.value
