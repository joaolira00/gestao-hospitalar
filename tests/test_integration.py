import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.auth_service import get_current_user
from database.database import Base, get_db
from main import app
from models.pacient_model import Pacient

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_current_user():
    return {
        "username": "user_teste",
        "role": "PACIENT" 
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
        birth_date="2000-01-01",
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


def test_search_pacient_forbidden(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "recep_teste",
        "role": "RECEPCIONISTA"
    }
    response = client.get("/pacients/search-patient/", params={"id": 9999})
    assert response.status_code == 404
    app.dependency_overrides.pop(get_current_user)