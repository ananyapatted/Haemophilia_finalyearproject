from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from .. import db
from ..database.models import Donor
from datetime import datetime
from ..utils.utils import is_doctor, is_patient_or_doctor
from sqlalchemy import or_, and_
from ..utils.utils import convert_datetime_to_mysql_format

donors_bp = Blueprint('donors_bp', __name__)

def validate_keys(data, required_keys):
    missing_keys = [key for key in required_keys if key not in data]
    return missing_keys

# GET: Retrieve all donor data
@donors_bp.route('/donors', methods=['GET'])
@jwt_required()
def get_all_donors():
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    donors = Donor.query.all()
    donors_list = [{
        'id': donor.id,
        'donor_name': donor.donor_name,
        'donor_id': donor.donor_id,
        'receiver_id': donor.receiver_id,
        'receiver_name': donor.receiver_name,
        'date': donor.date.isoformat(),
        'type': donor.type,
        'blood_grp': donor.blood_grp,
        'assignee_name': donor.assignee_name,
        'assignee_id': donor.assignee_id
    } for donor in donors]
    return jsonify(donors_list)

# GET: Retrieve all donations by a specific user ID
@donors_bp.route('/donors/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_donations_by_user(user_id):
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    try:
        donations = Donor.query.filter_by(donor_id=user_id).all()
        return jsonify([{
            'id': donation.id,
            'donor_name': donation.donor_name,
            'donor_id': donation.donor_id,
            'receiver_id': donation.receiver_id,
            'receiver_name': donation.receiver_name,
            'date': donation.date.isoformat(),
            'type': donation.type,
            'blood_grp': donation.blood_grp
        } for donation in donations])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# GET: Retrieve single donor data by ID
@donors_bp.route('/donors/<int:donor_id>', methods=['GET'])
@jwt_required()
def get_donor(donor_id):
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    try:
        donor = Donor.query.get_or_404(donor_id)
        return jsonify({
            'id': donor.id,
            'donor_name': donor.donor_name,
            'donor_id': donor.donor_id,
            'receiver_id': donor.receiver_id,
            'receiver_name': donor.receiver_name,
            'date': donor.date.isoformat(),
            'type': donor.type,
            'blood_grp': donor.blood_grp,
            'assignee_name': donor.assignee_name,
            'assignee_id': donor.assignee_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# GET: Retrieve donor data with no assigned receiver
@donors_bp.route('/donors/no-receiver', methods=['GET'])
@jwt_required()
def get_donors_without_receiver():
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    donors = Donor.query.filter(or_(Donor.receiver_id == None, Donor.receiver_name == None)).all()
    donors_list = [{
        'id': donor.id,
        'donor_name': donor.donor_name,
        'donor_id': donor.donor_id,
        # 'receiver_id': donor.receiver_id,
        # 'receiver_name': donor.receiver_name,
        'date': donor.date.isoformat(),
        'type': donor.type,
        'blood_grp': donor.blood_grp
        # 'assignee_name': donor.assignee_name,
        # 'assignee_id': donor.assignee_id
    } for donor in donors]
    return jsonify(donors_list)

# GET: Retrieve donor data where receiver_id and receiver_name are not null
@donors_bp.route('/donors/with-receiver', methods=['GET'])
@jwt_required()
def get_donors_with_receiver():
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    donors = Donor.query.filter(and_(Donor.receiver_id != None, Donor.receiver_name != None)).all()
    donors_list = [{
        'id': donor.id,
        'donor_name': donor.donor_name,
        'donor_id': donor.donor_id,
        'receiver_id': donor.receiver_id,
        'receiver_name': donor.receiver_name,
        'date': donor.date.isoformat(),
        'type': donor.type,
        'blood_grp': donor.blood_grp,
        'assignee_name': donor.assignee_name,
        'assignee_id': donor.assignee_id
    } for donor in donors]
    return jsonify(donors_list)


# POST: Create new donor data
@donors_bp.route('/donors', methods=['POST'])
@jwt_required()
def create_donor():
    if not is_patient_or_doctor():
        return jsonify({'message': 'Permission denied'}), 403

    data = request.get_json()
    required_keys = ['donor_name', 'donor_id', 'date', 'type', 'blood_grp']
    missing_keys = validate_keys(data, required_keys)
    if missing_keys:
        return jsonify({'message': f'Missing key(s): {", ".join(missing_keys)}'}), 400
    
    try:
        # Generate a unique ID based on the current date and timestamp
        # Format: YYYYMMDDHHMMSS (Year, Month, Day, Hour, Minute, Second)
        unique_id = datetime.now().strftime("%Y%d%H%S")
        new_donor = Donor(
            donor_name=data['donor_name'],
            id=unique_id,
            donor_id=data['donor_id'],
            date=convert_datetime_to_mysql_format(data.get('date')),
            type=data['type'],
            blood_grp=data['blood_grp'],
            # Conditionally include optional fields, defaulting to None
            receiver_id=data.get('receiver_id'),
            receiver_name=data.get('receiver_name'),
            assignee_name=data.get('assignee_name'),
            assignee_id=data.get('assignee_id')
        )
        db.session.add(new_donor)
        db.session.commit()
        return jsonify({'message': 'New donor data created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# PUT: Modify existing donor data
@donors_bp.route('/donors/<int:donor_id>', methods=['PUT'])
@jwt_required()
def update_donor(donor_id):
    data = request.get_json()
    required_keys = ['donor_name', 'date', 'type', 'blood_grp']
    missing_keys = validate_keys(data, required_keys)
    if missing_keys:
        return jsonify({'message': f'Missing key(s): {", ".join(missing_keys)}'}), 400
    
    try:
        donor = Donor.query.get_or_404(donor_id)
        donor.donor_name = data['donor_name']
        donor.receiver_id = data.get('receiver_id')
        donor.receiver_name = data.get('receiver_name')
        donor.date = convert_datetime_to_mysql_format(data.get('date'))
        donor.type = data['type']
        donor.blood_grp = data['blood_grp']
        donor.assignee_name = data.get('assignee_name')
        donor.assignee_id = data.get('assignee_id')
        db.session.commit()
        return jsonify({'message': 'Donor data updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# DELETE: Delete donor data
@donors_bp.route('/donors/<int:donor_id>', methods=['DELETE'])
@jwt_required()
def delete_donor(donor_id):
    try:
        donor = Donor.query.get_or_404(donor_id)
        db.session.delete(donor)
        db.session.commit()
        return jsonify({'message': 'Donor data deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
