from flask import Blueprint, request, jsonify
from datetime import datetime, date
from models import Transaction, User
from database import Session
from utils.validators import Validator
from risk_engine import RiskEngine
from flask import current_app

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/log', methods=['POST'])
def log_purchase():
    try:
        from flask import current_app
        current_app.broadcast_transaction({
            'transaction': result,
            'user': {
                'user_id': user.user_id,
                'name': user.name,
                'risk_level': user.risk_level
            },
            'patterns': [{'type': p[0], 'confidence': p[1]} for p in patterns]
        })
    except Exception as e:
        print(f"Websocket broadcast error: {e}")
    
    """Log a new alcohol purchase"""
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
        
        # Check if user is blocked
        if user.is_blocked:
            db.close()
            return jsonify({'error': 'User is blocked from purchasing'}), 403
        
        # Validate units
        units = data.get('units')
        if not units:
            # Calculate units if not provided
            quantity_ml = data.get('quantity_ml')
            abv = data.get('abv_percentage')
            if quantity_ml and abv:
                units = Validator.calculate_units(quantity_ml, abv)
            else:
                db.close()
                return jsonify({'error': 'Units or (quantity_ml + abv_percentage) required'}), 400
        
        valid, error = Validator.validate_units(units)
        if not valid:
            db.close()
            return jsonify({'error': error}), 400
        
        # Check daily limit
        allowed, current, remaining = RiskEngine.check_daily_limit(user.user_id, units, db)
        
        if not allowed:
            db.close()
            return jsonify({
                'error': 'Daily limit exceeded',
                'current_units_today': current,
                'limit': current + remaining,
                'attempted_units': units
            }), 403
        
        # Create transaction
        transaction = Transaction(
            user_id=data['user_id'],
            shop_id=data.get('shop_id'),
            alcohol_type=data.get('alcohol_type'),
            brand=data.get('brand'),
            quantity_ml=data.get('quantity_ml'),
            units=units,
            abv_percentage=data.get('abv_percentage'),
            amount_paid=data.get('amount_paid'),
            payment_method=data.get('payment_method'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.add(transaction)
        
        # Update user stats
        user.total_purchases += 1
        user.total_units_consumed += units
        user.last_purchase_date = date.today()
        
        # Update daily limit
        RiskEngine.update_daily_limit(user.user_id, units, db)
        
        # Recalculate risk score
        RiskEngine.calculate_risk_score(user.user_id, db)
        
        # Run pattern detection
        patterns = RiskEngine.run_pattern_detection(user.user_id, db)
        
        db.commit()
        
        result = transaction.to_dict()
        db.close()
        
        return jsonify({
            'message': 'Purchase logged successfully',
            'transaction': result,
            'patterns_detected': [{'type': p[0], 'confidence': p[1]} for p in patterns],
            'remaining_units_today': remaining - units
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction by ID"""
    try:
        db = Session()
        transaction = db.query(Transaction).filter_by(transaction_id=transaction_id).first()
        
        if not transaction:
            db.close()
            return jsonify({'error': 'Transaction not found'}), 404
        
        result = transaction.to_dict()
        db.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transactions_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_transactions(user_id):
    """Get all transactions for a user"""
    try:
        db = Session()
        
        # Check if user exists
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Optional date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = db.query(Transaction).filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        transactions = query.order_by(Transaction.transaction_date.desc()).all()
        result = [t.to_dict() for t in transactions]
        
        db.close()
        
        return jsonify({
            'user_id': user_id,
            'count': len(result),
            'transactions': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transactions_bp.route('/recent', methods=['GET'])
def get_recent_transactions():
    """Get recent transactions across all users"""
    try:
        db = Session()
        
        limit = request.args.get('limit', 50, type=int)
        
        transactions = db.query(Transaction).order_by(
            Transaction.transaction_date.desc()
        ).limit(limit).all()
        
        result = [t.to_dict() for t in transactions]
        db.close()
        
        return jsonify({
            'count': len(result),
            'transactions': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500