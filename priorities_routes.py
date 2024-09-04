from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from .. import db
from ..database.models import MedicalHistory, Appointment, User
from ..utils.severity_dosage import severity_calulation
from ..utils.utils import convert_datetime_to_mysql_format, calculate_age
from ..ml.ml_model import predict_priority

priorities_bp = Blueprint('priorities_bp', __name__)

@priorities_bp.route('/priorities', methods=['GET'])
@jwt_required()
def get_all_priorities():
    # Get all medical histories where the doctor_id matches the given user_id
    histories_with_users = db.session.query(MedicalHistory).join(
        User, MedicalHistory.user_id == User.id).all()

    # Prepare the response data
    history_data = []
    for user_id, history in histories_with_users.items():
        user = history.user
        age = calculate_age(user.date_of_birth)
        history_data.append({
            'id': history.id,
            'user_name': user.name,
            'user_id': history.user_id,
            'age': age,
            'disease': history.disease,
            'diagnosis_date': history.diagnosis_date.isoformat() if history.diagnosis_date else None,
            'symptoms': history.symptoms,
            'weight': history.weight,
            'severity': history.severity,
            'factor': history.factor,
            'aptt_plasma': history.aptt_plasma,
            'diet': history.diet,
            'habits': history.habits,
            'medicines': history.medicines,
            'current_appointment_date': history.current_appointment_date.isoformat() if history.current_appointment_date else None,
            'next_appointment_date': history.next_appointment_date.isoformat() if history.next_appointment_date else None,
            'doctor_id': history.doctor_id,
            'allergies': history.allergies,
            'chronic_conditions': history.chronic_conditions,
            'family_history': history.family_history,
            'immunization_records': history.immunization_records,
            'privacy_consent': history.privacy_consent,
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat()
        })

    return jsonify(history_data), 200

@priorities_bp.route('/priorities/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_priorities_by_user(user_id):
    # Get all medical histories where the doctor_id matches the given user_id
    histories_with_users = db.session.query(MedicalHistory).join(
        User, MedicalHistory.user_id == User.id).filter(MedicalHistory.doctor_id == user_id).all()
    print(histories_with_users)

    if not histories_with_users:
        return jsonify({"message": "No medical histories found for the given user_id"}), 404

    # Create a dictionary to keep track of the latest medical history for each user_id
    latest_histories = {}
    for history in histories_with_users:
        if history.user_id not in latest_histories or history.created_at > latest_histories[history.user_id].created_at:
            latest_histories[history.user_id] = history

    # Prepare the response data
    history_data = []
    for user_id, history in latest_histories.items():
        user = history.user
        age = calculate_age(user.date_of_birth)
        history_data.append({
            'id': history.id,
            'user_name': user.name,
            'user_id': history.user_id,
            'age': age,
            'disease': history.disease,
            'diagnosis_date': history.diagnosis_date.isoformat() if history.diagnosis_date else None,
            'symptoms': history.symptoms,
            'weight': history.weight,
            'severity': history.severity,
            'factor': history.factor,
            'aptt_plasma': history.aptt_plasma,
            'diet': history.diet,
            'habits': history.habits,
            'medicines': history.medicines,
            'current_appointment_date': history.current_appointment_date.isoformat() if history.current_appointment_date else None,
            'next_appointment_date': history.next_appointment_date.isoformat() if history.next_appointment_date else None,
            'doctor_id': history.doctor_id,
            'allergies': history.allergies,
            'chronic_conditions': history.chronic_conditions,
            'family_history': history.family_history,
            'immunization_records': history.immunization_records,
            'privacy_consent': history.privacy_consent,
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat()
        })

    priorities = predict_priority(history_data)
    return jsonify(priorities), 200