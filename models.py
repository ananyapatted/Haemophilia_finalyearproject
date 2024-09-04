from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from ..import db
from sqlalchemy.types import TypeDecorator, Text


class ListJSON(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None

class JSONEncodedDict(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(255), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver_name = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(255), nullable=False)
    blood_grp = db.Column(db.String(255), nullable=False)
    assignee_name = db.Column(db.String(255), nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_name = db.Column(db.String(255), nullable=False)
    requirement = db.Column(db.String(255), nullable=False)
    symptoms = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class MedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease = db.Column(db.Text, nullable=False)
    diagnosis_date = db.Column(db.Date, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    severity = db.Column(db.String(255), nullable=False)
    factor = db.Column(db.Integer, nullable=True)
    aptt_plasma = db.Column(db.String(255), nullable=False)
    diet = db.Column(db.Text, nullable=False)
    habits = db.Column(db.Text, nullable=True)
    medicines = db.Column(db.Text, nullable=False)
    current_appointment_date = db.Column(db.Date, nullable=False)
    next_appointment_date = db.Column(db.Date, nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    allergies = db.Column(db.Text, nullable=True)
    chronic_conditions = db.Column(db.Boolean, nullable=True)
    family_history = db.Column(db.Text, nullable=True)
    immunization_records = db.Column(db.Text, nullable=True)
    privacy_consent = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(255), nullable=False)
    patient_name = db.Column(db.String(255), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.Column(db.String(255), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    profession = db.Column(db.String(255), nullable=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationships
    donations = db.relationship('Donor', foreign_keys=[Donor.donor_id], backref='donor', lazy='dynamic')
    receipts = db.relationship('Donor', foreign_keys=[Donor.receiver_id], backref='receiver', lazy='dynamic')
    appointments = db.relationship('Appointment', foreign_keys=[Appointment.patient_id], backref='patient', lazy='dynamic')
    medical_histories = db.relationship('MedicalHistory', foreign_keys=[MedicalHistory.user_id], backref='user', lazy='dynamic')