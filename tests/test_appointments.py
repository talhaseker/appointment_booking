from http import HTTPStatus


def test_create_appointment_api(client, patient_id, doctor_id):
    # This request tries to schedule an appointment with the doctor with doctor_id and patient with patient_id
    response = client.post('/appointments', json={
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'start_time': '2023-06-15 14:45:00',
        'end_time': '2023-06-15 15:05:00'
    })
    # If successfully created the appointment then the service returns CREATED.
    assert response.status_code == HTTPStatus.CREATED

    # This request tries to create a conflicting appointment. So the request should be rejected.
    response = client.post('/appointments', json={
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'start_time': '2023-06-15 15:00:00',
        'end_time': '2023-06-15 15:30:00'
    })
    # This request should return status code BAD_REQUEST because of the overlapping times.
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_appointments_api(client, doctor_id):
    start_time = '2023-06-15 14:45:00'
    end_time = '2023-06-15 16:05:00'
    response = client.get(f'/appointments?doctor_id={doctor_id}&start_time={start_time}&end_time={end_time}')
    assert response.status_code == HTTPStatus.OK


def test_get_first_available_appointment_api(client, doctor_id):
    start_time = '2023-06-15 14:45:00'
    response = client.get(f'/appointments/first-available?doctor_id={doctor_id}&start_time={start_time}')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json)