from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from .. import db
from ..database.models import Request, Appointment
from datetime import datetime
from ..utils.utils import validate_keys
from ..utils.utils import convert_datetime_to_mysql_format

# Define the Blueprint
appointments_bp = Blueprint('appointments_bp', __name__)

# GET: Retrieve all appointment data
@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_all_appointments():
    try:
        appointments = Appointment.query.all()
        appointments_list = [{
            'id': appointment.id,
            'patient_name':appointment.patient_name,
            'doctor_name':appointment.doctor_name,
            'doctor_id': appointment.doctor_id,
            'appointment_date': appointment.appointment_date.isoformat(),
            'patient_id': appointment.patient_id,
            'symptoms': appointment.symptoms
        } for appointment in appointments]
        return jsonify(appointments_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# GET: Retrieve appointment data by patient_id
@appointments_bp.route('/appointments/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_appointments_by_patient(patient_id):
    try:
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        if not appointments:
            return jsonify({'message': 'No appointments found for the given patient_id'}), 404
        appointments_list = [{
            'id': appointment.id,
            'patient_name':appointment.patient_name,
            'doctor_name':appointment.doctor_name,
            'doctor_id': appointment.doctor_id,
            'appointment_date': appointment.appointment_date.isoformat(),
            'patient_id': appointment.patient_id,
            'symptoms': appointment.symptoms
        } for appointment in appointments]
        return jsonify(appointments_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# GET: Retrieve appointment data by doctor_id
@appointments_bp.route('/appointments/doctor/<int:doctor_id>', methods=['GET'])
@jwt_required()
def get_appointments_by_doctor(doctor_id):
    try:
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        if not appointments:
            return jsonify({'message': 'No appointments found for the given doctor_id'}), 200
        appointments_list = [{
            'id': appointment.id,
            'patient_name':appointment.patient_name,
            'doctor_name':appointment.doctor_name,
            'doctor_id': appointment.doctor_id,
            'appointment_date': appointment.appointment_date.isoformat(),
            'patient_id': appointment.patient_id,
            'symptoms': appointment.symptoms
        } for appointment in appointments]
        print(appointments_list)
        return jsonify(appointments_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# POST: Create new appointment data
@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    data = request.get_json()
    required_keys = ['doctor_id', 'appointment_date', 'patient_id', 'symptoms','request_id','doctor_name','patient_name']
    missing_keys = validate_keys(data, required_keys)
    if missing_keys:
        return jsonify({'message': f'Missing key(s): {", ".join(missing_keys)}'}), 400
    
    try:
        new_appointment = Appointment(
            patient_name=data['patient_name'],
            doctor_name=data['doctor_name'],
            doctor_id=data['doctor_id'],
            appointment_date=convert_datetime_to_mysql_format(data['appointment_date']),
            patient_id=data['patient_id'],
            symptoms=data['symptoms']
        )
        #TODO rmeove this
        request_data = Request.query.get_or_404(data['request_id'])
        db.session.delete(request_data)
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({'message': 'New appointment created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# PUT: Modify existing appointment data
@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    data = request.get_json()
    required_keys = ['doctor_id', 'appointment_date', 'patient_id', 'symptoms']
    missing_keys = validate_keys(data, required_keys)
    if missing_keys:
        return jsonify({'message': f'Missing key(s): {", ".join(missing_keys)}'}), 400
    
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.patient_name=data['patient_name']
        appointment.doctor_name=data['doctor_name']
        appointment.doctor_id = data['doctor_id']
        appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment.patient_id = data['patient_id']
        appointment.symptoms = data['symptoms']
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# DELETE: Delete appointment data
@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
