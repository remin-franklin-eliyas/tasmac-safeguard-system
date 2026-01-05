from flask import Blueprint, request, jsonify
from models import Incident, User
from database import Session

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/report', methods=['POST'])
def report_incident():
    """Report a new incident"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = Session()
        
        # Validate user exists
        user = db.query(User).filter_by(user_id=data.get('user_id')).first()
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Create incident
        incident = Incident(
            user_id=data['user_id'],
            incident_type=data.get('incident_type'),
            incident_date=data.get('incident_date'),
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            police_report_number=data.get('police_report_number'),
            description=data.get('description'),
            severity=data.get('severity', 'Medium'),
            reported_by=data.get('reported_by')
        )
        
        db.add(incident)
        db.commit()
        
        result = incident.to_dict()
        db.close()
        
        return jsonify({
            'message': 'Incident reported successfully',
            'incident': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@incidents_bp.route('/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get incident by ID"""
    try:
        db = Session()
        incident = db.query(Incident).filter_by(incident_id=incident_id).first()
        
        if not incident:
            db.close()
            return jsonify({'error': 'Incident not found'}), 404
        
        result = incident.to_dict()
        db.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@incidents_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_incidents(user_id):
    """Get all incidents for a user"""
    try:
        db = Session()
        
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        incidents = db.query(Incident).filter_by(user_id=user_id).order_by(
            Incident.incident_date.desc()
        ).all()
        
        result = [i.to_dict() for i in incidents]
        db.close()
        
        return jsonify({
            'user_id': user_id,
            'count': len(result),
            'incidents': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@incidents_bp.route('/all', methods=['GET'])
def get_all_incidents():
    """Get all incidents with optional filtering"""
    try:
        db = Session()
        
        severity = request.args.get('severity')
        incident_type = request.args.get('incident_type')
        
        query = db.query(Incident)
        
        if severity:
            query = query.filter_by(severity=severity)
        if incident_type:
            query = query.filter_by(incident_type=incident_type)
        
        incidents = query.order_by(Incident.incident_date.desc()).all()
        result = [i.to_dict() for i in incidents]
        
        db.close()
        
        return jsonify({
            'count': len(result),
            'incidents': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500