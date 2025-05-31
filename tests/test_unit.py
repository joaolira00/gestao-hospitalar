import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db
from main import app
from models.pacient_model import Pacient
from models.staff_model import Staff
from models.appointment_model import AppointmentStatus
from datetime import datetime, timedelta, timezone
from services.auth_service import get_current_user
from dotenv import load_dotenv
from sqlalchemy import text
from services.auth_service import get_current_user
from models.staff_model import Staff
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


def fake_current_user():
    return {"username": "john doe", "role": "RECEPCIONISTA"}

app.dependency_overrides[get_current_user] = fake_current_user
client = TestClient(app)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_search_patient_by_id_not_found(db_session):
    p = create_test_pacient(db_session)
    response = client.get(f"/patients/search-patient?id=9999")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Nenhum paciente encontrado."


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


def create_test_pacient2(db, cpf="12345678127"):
    pacient = Pacient(
        id=6,
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
    response = client.get(f"/patients/search-patient?id={p.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == p.id


def test_search_patient_by_name_multiple_results(db_session):
    p = create_test_pacient(db_session)
    p2 = create_test_pacient2(db_session)
    response = client.get(f"/patients/search-patient?name={p.full_name}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["full_name"] == p.full_name
    assert data[1]["full_name"] == p2.full_name


@pytest.mark.parametrize("cpf", ["11122233381", "49572057207"])
def test_add_new_pacient(cpf):
    payload = {
        "id": 9,
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
    response = client.post("/patients/add-new-patient", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Usuário criado com sucesso."


def test_add_existing_pacient(db_session):
    paciente = Pacient(
        full_name="Paciente Existente",
        birth_date="2000-01-01",
        cpf="12345678901",
        hashed_password="senhaQualquer",
        gender="Feminino",
        phone_number="11988887777",
        address="Rua X",
        email="",
        blood_type="A-",
        known_allergies=""
    )
    db_session.add(paciente)
    db_session.commit()

    payload = {
        "full_name": "Novo Paciente",
        "birth_date": "20000101",
        "cpf": "12345678901",
        "hashed_password": "password",
        "gender": "Feminino",
        "phone_number": "11988887777",
        "address": "Rua Nova",
        "email": "",
        "blood_type": "A-",
        "known_allergies": ""
    }
    response = client.post(
        "/patients/add-new-patient",
        json=payload
    )

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "CPF já cadastrado."


def test_add_pacient_invalid_data(db_session):
    payload = {
        "full_name": "Novo Paciente",
        "birth_date": "20000101",
        "cpf": "12345678901",
        "hashed_password": "12",
        "gender": "Feminino",
        "phone_number": "11988887777",
        "address": "Rua Nova",
        "email": "",
        "blood_type": "A-",
        "known_allergies": ""
    }
    response = client.post(
        "/patients/add-new-patient",
        json=payload
    )

    assert response.status_code == 422


def test_update_pacient_concurrent(db_session):
    p = create_test_pacient(db_session, cpf="22233344455")
    payload = {"full_name": "Alterado", 
               "birth_date": "01012003",
               "phone_number": "91912345678",
               "address": "Montreal",
               "version_id": p.version_id - 1}
    response = client.patch(f"/patients/update-patient/{p.id}", json=payload)
    assert response.status_code == 409


def test_update_pacient_not_found(db_session):
    p = create_test_pacient(db_session, cpf="22233344455")
    payload = {"full_name": "Alterado", 
               "birth_date": "01012003",
               "phone_number": "91912345678",
               "address": "Montreal",
               "version_id": p.version_id - 1}
    response = client.patch(f"/patients/update-patient/999999", json=payload)
    assert response.status_code == 404


def test_update_pacient_success(db_session):
    p = create_test_pacient(db_session, cpf="22233344455")
    payload = {"full_name": "Alterado", 
               "birth_date": "01012003",
               "phone_number": "91912345678",
               "address": "Montreal",
               "email": "alterado@gmail.com",
               "version_id": p.version_id}
    response = client.patch(f"/patients/update-patient/{p.id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Usuário atualizado com sucesso."



def test_inactivate_patient(db_session):
    p = create_test_pacient(db_session, cpf="33344455566")
    payload = {"reason": "Motivo Teste"}
    response = client.post(f"/patients/inactivate-patient/{p.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["pacient_id"] == p.id
    assert data["inactivated_by"]



def test_schedule_appointment(db_session):
    p = create_test_pacient(db_session, cpf="44455566677")
    db_session.commit()
    db_session.refresh(p)

    doctor = Staff(username="Dr. Teste", cpf="99988871952", hashed_password="hsuhd82731", role="DOCTOR")
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