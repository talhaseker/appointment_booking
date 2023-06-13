from flask import Flask
import iniconfig
from datetime import time
from src.extensions import db
from src.endpoints.appointments import appointments
from src.endpoints.patient import patient_bp
from src.endpoints.home import home
from src.models import Doctor, WorkingHours


def integrate_doctors_data():
    for name in ["Strange", "Who"]:
        doc = db.session.query(Doctor).filter_by(name=name).first()
        if not doc:
            doc = Doctor(name=name)
            db.session.add(doc)
            db.session.commit()
            wh = WorkingHours(doctor_id=doc.id, day_of_week=0, start_time=time(hour=8), end_time=time(hour=17))
            db.session.add(wh)
            wh = WorkingHours(doctor_id=doc.id, day_of_week=1, start_time=time(hour=8), end_time=time(hour=17))
            db.session.add(wh)
            wh = WorkingHours(doctor_id=doc.id, day_of_week=2, start_time=time(hour=8), end_time=time(hour=17))
            db.session.add(wh)
            wh = WorkingHours(doctor_id=doc.id, day_of_week=3, start_time=time(hour=8), end_time=time(hour=17))
            db.session.add(wh)
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
    app.register_blueprint(patient_bp)
    app.register_blueprint(appointments)

    # print(app.url_map)

    return app
