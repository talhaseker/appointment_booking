from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models import Appointment, Doctor, Patient, WorkingHours
from webargs import fields
from webargs.flaskparser import use_args

appointments = Blueprint('/appointments', __name__, url_prefix="/appointments")


@appointments.route('/', methods=['POST'])
@use_args({'patient_id': fields.Int(), 'doctor_id': fields.Int(),
           'start_time': fields.String(), 'end_time': fields.String()})
def create_appointment(args):
    print(args)
    patient_id = args.get('patient_id')
    doctor_id = args.get('doctor_id')
    start_time = datetime.strptime(args.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.get('end_time'), '%Y-%m-%d %H:%M:%S')
    print(start_time.weekday())
    # Check if the patient exists
    patient = Patient.query.get(doctor_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), HTTPStatus.NOT_FOUND

    # Check if the doctor exists
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), HTTPStatus.NOT_FOUND

    # Check if the doctor works on those hours.
    working_hours = WorkingHours.query.filter(
        WorkingHours.day_of_week == start_time.weekday(),
        WorkingHours.start_time <= start_time.time(),
        WorkingHours.end_time >= end_time.time()
    ).first()
    if not working_hours:
        return jsonify({"error": "Doctor is not available at that time!"}), HTTPStatus.NOT_FOUND

    # Check if the appointment time conflicts with existing appointments
    if db.session.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time < end_time, Appointment.end_time > start_time
    ).first():
        return jsonify({'message': 'Appointment time conflict'}), HTTPStatus.BAD_REQUEST

    # Create a new appointment
    new_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment created successfully',
                    "appointment": {"id": new_appointment.id}}), HTTPStatus.CREATED


@appointments.route('/', methods=['GET'])
@use_args({'doctor_id': fields.Int(), 'start_time': fields.String(),
           'end_time': fields.String()}, location="query")
def get_appointments(args):
    doctor_id = args.get('doctor_id')
    start_time = datetime.strptime(args.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.get('end_time'), '%Y-%m-%d %H:%M:%S')

    appointments = db.session.query(Appointment).query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time >= start_time,
        Appointment.end_time <= end_time
    ).all()

    appointment_list = [appointment.json() for appointment in appointments]

    return jsonify(appointment_list), HTTPStatus.OK


@appointments.route('/first-available', methods=['GET'])
@use_args({'start_time': fields.String(), 'duration': fields.Int()}, location="query")
def get_first_available_appointment(args):
    start_time = datetime.strptime(args.get('start_time'), '%Y-%m-%d %H:%M:%S')
    duration = args.get('duration')

    available_times = []

    doctors = Doctor.query.all()

    for doctor in doctors:
        working_hours = WorkingHours.query.filter_by(doctor_id=doctor.id).all()

        for working_hour in working_hours:
            day_of_week = working_hour.day_of_week
            start_time_hour = working_hour.start_time.hour
            start_time_min = working_hour.start_time.minute
            end_time_hour = working_hour.end_time.hour
            end_time_min = working_hour.end_time.minute

            current_date = start_time.date()
            current_time = start_time.time()

            while current_date <= start_time.date():
                if current_date == start_time.date():
                    if (
                            current_time.hour < end_time_hour or
                            (current_time.hour == end_time_hour and current_time.minute <= end_time_min)
                    ):
                        start_datetime = datetime.combine(current_date, current_time)
                        end_datetime = start_datetime + timedelta(minutes=duration)

                        appointments = Appointment.query.filter(
                            Appointment.doctor_id == doctor.id,
                            Appointment.start_time >= start_datetime.replace(hour=0, minute=0),
                            Appointment.start_time < (start_datetime + timedelta(days=1)).replace(hour=0, minute=0)
                        ).all()

                        appointment_intervals = [
                            (appointment.start_time, appointment.end_time)
                            for appointment in appointments
                        ]

                        if not has_conflict(appointment_intervals, start_datetime, end_datetime):
                            available_times.append((start_datetime, doctor.id))
                else:
                    if (
                            start_time_hour < end_time_hour or
                            (start_time_hour == end_time_hour and start_time_min <= end_time_min)
                    ):
                        start_datetime = datetime.combine(current_date, datetime.min.time())
                        start_datetime = start_datetime.replace(hour=start_time_hour, minute=start_time_min)
                        end_datetime = start_datetime + timedelta(minutes=duration)

                        appointments = Appointment.query.filter(
                            Appointment.doctor_id == doctor.id,
                            Appointment.start_time >= start_datetime.replace(hour=0, minute=0),
                            Appointment.start_time < (start_datetime + timedelta(days=1)).replace(hour=0, minute=0)
                        ).all()

                        appointment_intervals = [
                            (appointment.start_time, appointment.end_time)
                            for appointment in appointments
                        ]

                        if not has_conflict(appointment_intervals, start_datetime, end_datetime):
                            available_times.append((start_datetime, doctor.id))

                current_date += timedelta(days=1)
                current_time = datetime.min.time()

    if available_times:
        available_times.sort(key=lambda x: x[0])
        first_available = available_times[0]
        return jsonify({'first_available': first_available[0].strftime('%Y-%m-%d %H:%M:%S'),
                        "doctor_id": first_available[1]}), HTTPStatus.OK

    return jsonify({'message': 'No available appointments found'}), HTTPStatus.NOT_FOUND


def has_conflict(appointment_intervals, start_datetime, end_datetime):
    for interval in appointment_intervals:
        if interval[0] < end_datetime and start_datetime < interval[1]:
            return True
    return False
