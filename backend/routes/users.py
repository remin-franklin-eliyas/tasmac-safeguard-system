from flask import Blueprint, request, jsonify
from models import User
from database import Session
from utils.validators import Validator
from risk_engine import RiskEngine

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate Aadhaar
        valid, error = Validator.validate_aadhaar(data.get('aadhaar_mock'))
        if not valid:
            return jsonify({'error': error}), 400
        
        # Validate age
        valid, error = Validator.validate_age(data.get('age'))
        if not valid:
            return jsonify({'error': error}), 400
        
        # Validate phone (optional)
        if data.get('phone'):
            valid, error = Validator.validate_phone(data.get('phone'))
            if not valid:
                return jsonify({'error': error}), 400
        
        db = Session()
        
        # Check if Aadhaar already exists
        existing = db.query(User).filter_by(aadhaar_mock=data['aadhaar_mock']).first()
        if existing:
            db.close()
            return jsonify({'error': 'User with this Aadhaar already exists'}), 409
        
        # Create new user
        user = User(
            aadhaar_mock=data['aadhaar_mock'],
            name=data.get('name', ''),
            age=data['age'],
            address=data.get('address'),
            phone=data.get('phone')
        )
        
        db.add(user)
        db.commit()
        
        result = user.to_dict()
        db.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        db = Session()
        user = db.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        result = user.to_dict()
        db.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/', methods=['GET'])
def get_all_users():
    """Get all users with optional filtering"""
    try:
        db = Session()
        
        # Optional filters
        risk_level = request.args.get('risk_level')
        is_blocked = request.args.get('is_blocked')
        
        query = db.query(User)
        
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        
        if is_blocked is not None:
            query = query.filter_by(is_blocked=is_blocked.lower() == 'true')
        
        users = query.all()
        result = [user.to_dict() for user in users]
        
        db.close()
        
        return jsonify({
            'count': len(result),
            'users': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/risk', methods=['GET'])
def get_user_risk(user_id):
    """Calculate and return user's risk score"""
    try:
        db = Session()
        user = db.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Calculate risk score
        score, level, factors = RiskEngine.calculate_risk_score(user_id, db)
        
        db.close()
        
        return jsonify({
            'user_id': user_id,
            'risk_score': score,
            'risk_level': level,
            'contributing_factors': factors
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/block', methods=['POST'])
def block_user(user_id):
    """Block a user"""
    try:
        db = Session()
        user = db.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        user.is_blocked = True
        db.commit()
        
        result = user.to_dict()
        db.close()
        
        return jsonify({
            'message': 'User blocked successfully',
            'user': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/unblock', methods=['POST'])
def unblock_user(user_id):
    """Unblock a user"""
    try:
        db = Session()
        user = db.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        user.is_blocked = False
        db.commit()
        
        result = user.to_dict()
        db.close()
        
        return jsonify({
            'message': 'User unblocked successfully',
            'user': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500