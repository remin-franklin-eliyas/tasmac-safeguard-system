from flask import Blueprint, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
from models import User, Transaction, Incident, Alert, PatternFlag
from database import Session

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get overall system statistics"""
    try:
        db = Session()
        
        # User statistics
        total_users = db.query(User).count()
        blocked_users = db.query(User).filter_by(is_blocked=True).count()
        
        risk_distribution = db.query(
            User.risk_level,
            func.count(User.user_id)
        ).group_by(User.risk_level).all()
        
        # Transaction statistics
        total_transactions = db.query(Transaction).count()
        
        # Recent transactions (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_transactions = db.query(Transaction).filter(
            Transaction.transaction_date >= cutoff_date
        ).count()
        
        # Total units consumed
        total_units = db.query(func.sum(Transaction.units)).scalar() or 0
        
        # Incident statistics
        total_incidents = db.query(Incident).count()
        recent_incidents = db.query(Incident).filter(
            Incident.incident_date >= cutoff_date.date()
        ).count()
        
        # Active alerts
        active_alerts = db.query(Alert).filter_by(acknowledged=False).count()
        
        # Pattern flags
        active_patterns = db.query(PatternFlag).filter_by(reviewed=False).count()
        
        db.close()
        
        return jsonify({
            'users': {
                'total': total_users,
                'blocked': blocked_users,
                'risk_distribution': dict(risk_distribution)
            },
            'transactions': {
                'total': total_transactions,
                'last_30_days': recent_transactions,
                'total_units_consumed': float(total_units)
            },
            'incidents': {
                'total': total_incidents,
                'last_30_days': recent_incidents
            },
            'alerts': {
                'active': active_alerts
            },
            'patterns': {
                'active_flags': active_patterns
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/trends/purchases', methods=['GET'])
def get_purchase_trends():
    """Get purchase trends over time"""
    try:
        db = Session()
        
        days = request.args.get('days', 30, type=int)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Daily purchase counts
        daily_stats = db.query(
            func.date(Transaction.transaction_date).label('date'),
            func.count(Transaction.transaction_id).label('count'),
            func.sum(Transaction.units).label('total_units')
        ).filter(
            Transaction.transaction_date >= cutoff_date
        ).group_by(
            func.date(Transaction.transaction_date)
        ).order_by('date').all()
        
        result = [{
            'date': str(stat.date),
            'purchase_count': stat.count,
            'total_units': float(stat.total_units or 0)
        } for stat in daily_stats]
        
        db.close()
        
        return jsonify({
            'period_days': days,
            'trends': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/high-risk-users', methods=['GET'])
def get_high_risk_users():
    """Get list of high-risk users"""
    try:
        db = Session()
        
        high_risk_users = db.query(User).filter_by(risk_level='Red').all()
        result = [user.to_dict() for user in high_risk_users]
        
        db.close()
        
        return jsonify({
            'count': len(result),
            'users': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500