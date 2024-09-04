from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from .. import db
from ..database.models import MedicalHistory, Appointment, User
from ..utils.severity_dosage import severity_calulation
from ..utils.utils import convert_datetime_to_mysql_format, calculate_age

medical_history_bp = Blueprint('medical_history_bp', __name__)

@medical_history_bp.route('/medical_histories', methods=['GET'])
@jwt_required()
def get_all_medical_histories():
    # Explicitly specify the join condition between MedicalHistory and User
    histories_with_users = db.session.query(MedicalHistory).join(
        User, MedicalHistory.user_id == User.id).all()

    # Generate a list of dictionary objects containing the data to jsonify
    history_data = []
    for history in histories_with_users:
        user = history.user  # Accessing the user details through the relationship
        history_data.append({
            'id': history.id,
            'user_name': user.name,
            'user_id': history.user_id,
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

@medical_history_bp.route('/medical_histories/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_medical_histories_by_user(user_id):

    histories_with_users = db.session.query(MedicalHistory).join(
        User, MedicalHistory.user_id == User.id).filter(MedicalHistory.user_id == user_id).all()

    if not histories_with_users:
        return jsonify({"message": "No medical histories found for the given user_id"}), 404

    history_data = []
    for history in histories_with_users:
        user = history.user
        history_data.append({
            'id': history.id,
            'user_name': user.name,
            'user_id': history.user_id,
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


@medical_history_bp.route('/medical_histories/<int:id>', methods=['GET'])
@jwt_required()
def get_medical_history(id):
    history = MedicalHistory.query.get_or_404(id)
    return jsonify({
        'id': history.id,
        'user_id': history.user_id,
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
    }), 200

@medical_history_bp.route('/medical_histories', methods=['POST'])
@jwt_required()
def create_medical_history():
    data = request.get_json()
    print(data)
    required_fields = ['appointment_id','user_id', 'disease', 'diagnosis_date', 'symptoms', 'severity', 'factor', 'aptt_plasma', 'diet', 'medicines', 'current_appointment_date', 'doctor_id', 'privacy_consent']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'message': 'Missing required fields', 'missing': missing_fields}), 400
    try:
        print(data)
        # new_history = MedicalHistory(**data)
        unique_id = datetime.now().strftime("%d%H%S%M")
        new_history = MedicalHistory(
            id= unique_id,
            user_id= data['user_id'],
            disease= data['disease'],
            diagnosis_date= convert_datetime_to_mysql_format(data.get('diagnosis_date')),
            symptoms= data['symptoms'],
            weight= data['weight'],
            severity= data['severity'],
            factor= data['factor'],
            aptt_plasma= data['aptt_plasma'],
            diet= data['diet'],
            habits= data['habits'],
            medicines= data['medicines'],
            current_appointment_date= convert_datetime_to_mysql_format(data.get('current_appointment_date')),
            next_appointment_date= convert_datetime_to_mysql_format(data.get('next_appointment_date')),
            doctor_id= data['doctor_id'],
            allergies= data['allergies'],
            chronic_conditions= data['chronic_conditions'],
            family_history= data['family_history'],
            immunization_records= data['immunization_records'],
            privacy_consent= data['privacy_consent']
        )
        appointment = Appointment.query.get_or_404(data['appointment_id'])
        db.session.delete(appointment)
        db.session.add(new_history)
        db.session.commit()
        return jsonify({'message': 'Medical history created successfully', 'id': new_history.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create medical history', 'details': str(e)}), 500

@medical_history_bp.route('/medical_histories/<int:id>', methods=['PUT'])
@jwt_required()
def update_medical_history(id):
    history = MedicalHistory.query.get_or_404(id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(history, key):
                setattr(history, key, value)
        db.session.commit()
        return jsonify({'message': 'Medical history updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update medical history', 'details': str(e)}), 500

@medical_history_bp.route('/medical_histories/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_medical_history(id):
    history = MedicalHistory.query.get_or_404(id)
    try:
        db.session.delete(history)
        db.session.commit()
        return jsonify({'message': 'Medical history deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete medical history', 'details': str(e)}), 500

@medical_history_bp.route('/medical_histories/report/<int:id>', methods=['GET'])
@jwt_required()
def generate_report(id):
    history = MedicalHistory.query.get_or_404(id)
    user = User.query.get_or_404(history.user_id)
    doctor = User.query.get_or_404(history.doctor_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = styles['Title']
    title_style.fontSize = 20
    title_style.spaceAfter = 20

    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceAfter=10
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 12
    normal_style.leading = 14

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    elements = []

    # Title
    elements.append(Paragraph("Medical History Report", title_style))
    elements.append(Spacer(1, 12))

    # Doctor Info
    elements.append(Paragraph(f"Doctor: {doctor.name}", subtitle_style))
    elements.append(Spacer(1, 12))

    # Patient Info
    patient_info_data = [
        ['Patient Name:', user.name],
        ['Age:', calculate_age(user.date_of_birth)],
        ['Gender:', user.gender]
    ]
    patient_info_table = Table(patient_info_data, colWidths=[100, 400])
    patient_info_table.setStyle(table_style)
    elements.append(patient_info_table)
    elements.append(Spacer(1, 20))

    # Medical History Details
    elements.append(Paragraph("Medical History Details", subtitle_style))
    history_data = [
        ['Disease:', history.disease],
        ['Diagnosis Date:', history.diagnosis_date],
        ['Symptoms:', history.symptoms],
        ['Weight (kg):', history.weight],
        ['Severity:', history.severity],
        ['Factor:', history.factor],
        ['APTT Plasma:', history.aptt_plasma],
        ['Diet:', history.diet],
        ['Habits:', history.habits],
        ['Medicines:', history.medicines],
        ['Current Appointment Date:', history.current_appointment_date],
        ['Next Appointment Date:', history.next_appointment_date],
        ['Allergies:', history.allergies],
        ['Chronic Conditions:', history.chronic_conditions],
        ['Family History:', history.family_history],
        ['Immunization Records:', history.immunization_records],
    ]
    history_table = Table(history_data, colWidths=[150, 350])
    history_table.setStyle(table_style)
    elements.append(history_table)
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), normal_style))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(send_file(buffer, as_attachment=True, download_name=f"Medical_History_Report_{history.id}.pdf"))
    response.headers['Content-Type'] = 'application/pdf'
    return response, 200

@medical_history_bp.route('/medical_histories/severity', methods=['POST'])
@jwt_required()
def generate_severity():
    data = request.get_json()
    print(data)
    severity, f8, f9 = severity_calulation(data)
    report = {
        'severity': severity,
        'f8': f8,
        'f9': f9
    }
    return jsonify(report), 200
