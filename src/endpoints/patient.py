from flask import Blueprint, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models import Patient
from webargs import fields
from webargs.flaskparser import use_args

patient = Blueprint('/patient', __name__)


@patient.route('/register', methods=['POST'])
@use_args({'name': fields.String(), 'email': fields.String(), 'password': fields.String()})
def register_patient(args):
    name = args.get('name')
    email = args.get('email')
    password = args.get('password')

    # Check if the email is already registered
    if db.session.query(Patient).filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), HTTPStatus.BAD_REQUEST

    # Create a new patient
    new_patient = Patient(name=name, email=email, password=password)
    db.session.add(new_patient)
    db.session.commit()
    resp = new_patient.json()
    del resp['password']
    resp.update({'message': 'Patient registered successfully'})
    return jsonify(resp), HTTPStatus.CREATED


@patient.route('/login', methods=['POST'])
@use_args({'email': fields.String(), 'password': fields.String()})
def login_patient(args):
    email = args.get('email')
    password = args.get('password')
    # Check if the email exists and the password is correct
    patient = db.session.query(Patient).filter_by(email=email).first()
    if not patient or patient.password != password:
        return jsonify({'message': 'Invalid email or password'}), HTTPStatus.NOT_FOUND

    return jsonify({'message': 'Login successful'}), HTTPStatus.OK
