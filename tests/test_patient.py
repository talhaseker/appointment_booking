from http import HTTPStatus


def test_register_patient_api(client):
    # This request should register a patient.
    response = client.post('/patient/register', json={
        'name': 'talha',
        'email': 'talhaseker@gmail.com',
        'password': '123456'
    })
    # If the registration successful, response status code should be CREATED.
    assert response.status_code == HTTPStatus.CREATED

    # This request should return success assuming user registered successfully.
    response = client.post('patient/login', json={
        'email': 'talhaseker@gmail.com',
        'password': '123456'
    })
    assert response.status_code == HTTPStatus.OK

    # Since the user exists. this case should return BAD_REQUEST status code.
    response = client.post('/patient/register', json={
        'name': 'talha',
        'email': 'talhaseker@gmail.com',
        'password': '123456'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_patient_api(client):
    # This request should return success assuming user registered successfully.
    response = client.post('patient/login', json={
        'email': 'talhaseker@gmail.com',
        'password': '123456'
    })
    assert response.status_code == HTTPStatus.OK
