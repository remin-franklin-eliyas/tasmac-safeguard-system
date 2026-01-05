from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Transaction, Incident, PatternFlag, DailyLimit, Alert
from config import Config

class RiskEngine:
    """Risk scoring and pattern detection engine"""
    
    @staticmethod
    def calculate_risk_score(user_id, db_session):
        """
        Calculate comprehensive risk score for a user
        Returns: (risk_score, risk_level, contributing_factors)
        """
        user = db_session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return None, None, []
        
        score = 0
        factors = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Factor 1: Purchase Frequency (0-25 points)
        transactions = db_session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= cutoff_date
        ).all()
        
        purchase_count = len(transactions)
        if purchase_count > Config.HIGH_FREQUENCY_THRESHOLD:
            score += 25
            factors.append(f"High frequency: {purchase_count} purchases/month")
        elif purchase_count > 10:
            score += 15
            factors.append(f"Elevated frequency: {purchase_count} purchases/month")
        
        # Factor 2: Volume Consumed (0-25 points)
        total_units = sum([t.units or 0 for t in transactions])
        if total_units > 100:
            score += 25
            factors.append(f"High volume: {total_units:.1f} units/month")
        elif total_units > 50:
            score += 15
            factors.append(f"Elevated volume: {total_units:.1f} units/month")
        
        # Factor 3: Time Patterns (0-15 points)
        early_morning = [t for t in transactions if t.transaction_date.hour < 10]
        late_night = [t for t in transactions if t.transaction_date.hour >= 22]
        
        if len(early_morning) > 5:
            score += 10
            factors.append(f"Early morning purchases: {len(early_morning)}")
        if len(late_night) > 5:
            score += 5
            factors.append(f"Late night purchases: {len(late_night)}")
        
        # Factor 4: Incident History (0-30 points)
        incidents = db_session.query(Incident).filter(
            Incident.user_id == user_id
        ).all()
        
        incident_score = 0
        for incident in incidents:
            if incident.severity == "High":
                incident_score += 15
            elif incident.severity == "Medium":
                incident_score += 10
            else:
                incident_score += 5
        
        score += min(incident_score, 30)
        if incidents:
            factors.append(f"Incident history: {len(incidents)} incidents")
        
        # Factor 5: Pattern Flags (0-20 points)
        pattern_flags = db_session.query(PatternFlag).filter(
            PatternFlag.user_id == user_id,
            PatternFlag.reviewed == False
        ).all()
        
        if pattern_flags:
            high_confidence = [f for f in pattern_flags if f.confidence_score > 0.7]
            flag_score = min(len(high_confidence) * 10 + len(pattern_flags) * 3, 20)
            score += flag_score
            factors.append(f"Pattern flags: {len(pattern_flags)} detected")
        
        # Factor 6: Daily Limit Violations (0-15 points)
        limit_violations = db_session.query(DailyLimit).filter(
            DailyLimit.user_id == user_id,
            DailyLimit.total_units_today > Config.DAILY_UNIT_LIMIT
        ).count()
        
        if limit_violations > 5:
            score += 15
            factors.append(f"Frequent limit violations: {limit_violations}")
        elif limit_violations > 0:
            score += 10
            factors.append(f"Limit violations: {limit_violations}")
        
        # Normalize to 0-100
        score = min(score, 100)
        
        # Determine Risk Level
        if score >= Config.RISK_THRESHOLD_RED:
            risk_level = "Red"
        elif score >= Config.RISK_THRESHOLD_YELLOW:
            risk_level = "Yellow"
        else:
            risk_level = "Green"
        
        # Update user record
        user.risk_score = score
        user.risk_level = risk_level
        db_session.commit()
        
        # Create alert if risk level changed
        if user.risk_level != risk_level:
            RiskEngine.create_alert(
                user_id, 
                "RiskLevelChange",
                f"Risk level changed to {risk_level}",
                "Warning" if risk_level == "Yellow" else "Critical",
                db_session
            )
        
        return score, risk_level, factors
    
    @staticmethod
    def detect_bulk_buying_pattern(user_id, db_session):
        """Detect bulk buying patterns (possible proxy for minors)"""
        cutoff_date = datetime.now() - timedelta(days=7)
        
        transactions = db_session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= cutoff_date
        ).all()
        
        high_volume = [t for t in transactions 
                      if t.quantity_ml and t.quantity_ml > Config.BULK_PURCHASE_THRESHOLD_ML]
        
        if len(high_volume) >= 3:
            confidence = min(len(high_volume) / 5, 1.0)
            
            # Create pattern flag
            pattern_flag = PatternFlag(
                user_id=user_id,
                pattern_type="BulkBuying",
                confidence_score=confidence,
                details={
                    "high_volume_count": len(high_volume),
                    "total_volume": sum([t.quantity_ml for t in high_volume]),
                    "period_days": 7
                }
            )
            db_session.add(pattern_flag)
            db_session.commit()
            
            return True, confidence
        
        return False, 0.0
    
    @staticmethod
    def detect_time_pattern(user_id, db_session):
        """Detect concerning time patterns"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        transactions = db_session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= cutoff_date
        ).all()
        
        morning = [t for t in transactions if 5 <= t.transaction_date.hour < 10]
        late_night = [t for t in transactions 
                     if t.transaction_date.hour >= 23 or t.transaction_date.hour < 5]
        
        if len(morning) > 7 or len(late_night) > 7:
            confidence = 0.7
            
            pattern_flag = PatternFlag(
                user_id=user_id,
                pattern_type="UnusualTimePattern",
                confidence_score=confidence,
                details={
                    "morning_count": len(morning),
                    "late_night_count": len(late_night),
                    "period_days": 30
                }
            )
            db_session.add(pattern_flag)
            db_session.commit()
            
            return True, confidence
        
        return False, 0.0
    
    @staticmethod
    def check_daily_limit(user_id, units, db_session):
        """
        Check if purchase would exceed daily limit
        Returns: (allowed, current_units, remaining_units)
        """
        today = datetime.now().date()
        
        daily_limit = db_session.query(DailyLimit).filter(
            DailyLimit.user_id == user_id,
            DailyLimit.date == today
        ).first()
        
        if not daily_limit:
            daily_limit = DailyLimit(
                user_id=user_id,
                date=today,
                total_units_today=0,
                purchase_count_today=0
            )
            db_session.add(daily_limit)
            db_session.commit()
        
        current_units = daily_limit.total_units_today
        new_total = current_units + units
        
        if new_total > Config.DAILY_UNIT_LIMIT:
            return False, current_units, Config.DAILY_UNIT_LIMIT - current_units
        
        return True, current_units, Config.DAILY_UNIT_LIMIT - new_total
    
    @staticmethod
    def update_daily_limit(user_id, units, db_session):
        """Update daily limit after successful purchase"""
        today = datetime.now().date()
        
        daily_limit = db_session.query(DailyLimit).filter(
            DailyLimit.user_id == user_id,
            DailyLimit.date == today
        ).first()
        
        if daily_limit:
            daily_limit.total_units_today += units
            daily_limit.purchase_count_today += 1
        else:
            daily_limit = DailyLimit(
                user_id=user_id,
                date=today,
                total_units_today=units,
                purchase_count_today=1
            )
            db_session.add(daily_limit)
        
        db_session.commit()
        
        # Create alert if limit exceeded
        if daily_limit.total_units_today > Config.DAILY_UNIT_LIMIT:
            RiskEngine.create_alert(
                user_id,
                "DailyLimitExceeded",
                f"Daily limit exceeded: {daily_limit.total_units_today:.1f} units",
                "Warning",
                db_session
            )
    
    @staticmethod
    def create_alert(user_id, alert_type, message, severity, db_session):
        """Create system alert"""
        alert = Alert(
            user_id=user_id,
            alert_type=alert_type,
            message=message,
            severity=severity
        )
        db_session.add(alert)
        db_session.commit()
        return alert
    
    @staticmethod
    def run_pattern_detection(user_id, db_session):
        """Run all pattern detection algorithms"""
        patterns_detected = []
        
        bulk, bulk_conf = RiskEngine.detect_bulk_buying_pattern(user_id, db_session)
        if bulk:
            patterns_detected.append(("BulkBuying", bulk_conf))
        
        time, time_conf = RiskEngine.detect_time_pattern(user_id, db_session)
        if time:
            patterns_detected.append(("UnusualTimePattern", time_conf))
        
        return patterns_detected