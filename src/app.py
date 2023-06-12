from flask import Flask
import iniconfig
from src.extensions import db
from src.endpoints.appointments import appointments
from src.endpoints.patient import patient
from src.endpoints.home import home
from src.models import Doctor


def integrate_doctors_data():
    for name in ["Strange", "Who"]:
        doc = Doctor.query.filter_by(name=name)
        if not doc:
            db.session.add(Doctor(name=name))
            db.session.commit()


def create_app():
    ini = iniconfig.IniConfig("../app.ini")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = ini['test']['sqlite_url']
    db.init_app(app)

    # We are doing a create all here to set up all the tables. Because we are using an in memory sqllite db, each
    # restart wipes the db clean, but does have the advantage of not having to worry about schema migrations.
    with app.app_context():
        db.create_all()
        integrate_doctors_data()

    app.register_blueprint(home)
    app.register_blueprint(patient)
    app.register_blueprint(appointments)
    return app
