import pytest
from http import HTTPStatus

from src.app import create_app
from src.extensions import db
from src.models import Doctor


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def patient_id(client):
    response = client.post('/patient/register', json={
        'name': 'talha',
        'email': 'talhaseker@gmail.com',
        'password': '123456'
    })
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response = client.post('patient/login', json={
            'email': 'talhaseker@gmail.com',
            'password': '123456'
        })
        return response.json['id']
    else:
        return response.json['id']


@pytest.fixture
def doctor_id(client):
    app = create_app()
    with app.app_context():
        doctor = Doctor.query.filter_by(name="Strange").first()
        if not doctor:
            doctor = Doctor(name="Strange")
            db.session.add(doctor)
            db.session.commit()
        return doctor.id

