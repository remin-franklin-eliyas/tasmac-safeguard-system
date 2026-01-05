from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, 
    Text, DECIMAL, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    aadhaar_mock = Column(String(12), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, CheckConstraint('age >= 18'), nullable=False)
    address = Column(Text)
    phone = Column(String(15))
    registration_date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(10), default='Green')
    is_blocked = Column(Boolean, default=False)
    last_purchase_date = Column(Date)
    total_purchases = Column(Integer, default=0)
    total_units_consumed = Column(Float, default=0.0)
    
    # Relationships
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    incidents = relationship('Incident', back_populates='user', cascade='all, delete-orphan')
    daily_limits = relationship('DailyLimit', back_populates='user', cascade='all, delete-orphan')
    pattern_flags = relationship('PatternFlag', back_populates='user', cascade='all, delete-orphan')
    alerts = relationship('Alert', back_populates='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'aadhaar_mock': self.aadhaar_mock,
            'name': self.name,
            'age': self.age,
            'address': self.address,
            'phone': self.phone,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'is_blocked': self.is_blocked,
            'total_purchases': self.total_purchases,
            'total_units_consumed': self.total_units_consumed
        }


class Shop(Base):
    __tablename__ = 'shops'
    
    shop_id = Column(Integer, primary_key=True)
    shop_name = Column(String(100), nullable=False)
    location = Column(Text, nullable=False)
    district = Column(String(50))
    pincode = Column(String(6))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    license_number = Column(String(50), unique=True)
    
    # Relationships
    transactions = relationship('Transaction', back_populates='shop')
    
    def to_dict(self):
        return {
            'shop_id': self.shop_id,
            'shop_name': self.shop_name,
            'location': self.location,
            'district': self.district,
            'pincode': self.pincode,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'license_number': self.license_number
        }


class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    shop_id = Column(Integer, ForeignKey('shops.shop_id', ondelete='CASCADE'), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    alcohol_type = Column(String(50))
    brand = Column(String(100))
    quantity_ml = Column(Integer)
    units = Column(Float)
    abv_percentage = Column(Float)
    amount_paid = Column(DECIMAL(10, 2))
    payment_method = Column(String(20))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    
    # Relationships
    user = relationship('User', back_populates='transactions')
    shop = relationship('Shop', back_populates='transactions')
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'shop_id': self.shop_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'alcohol_type': self.alcohol_type,
            'brand': self.brand,
            'quantity_ml': self.quantity_ml,
            'units': self.units,
            'abv_percentage': self.abv_percentage,
            'amount_paid': float(self.amount_paid) if self.amount_paid else None,
            'payment_method': self.payment_method
        }


class DailyLimit(Base):
    __tablename__ = 'daily_limits'
    
    limit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    total_units_today = Column(Float, default=0.0)
    purchase_count_today = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )
    
    # Relationships
    user = relationship('User', back_populates='daily_limits')
    
    def to_dict(self):
        return {
            'limit_id': self.limit_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'total_units_today': self.total_units_today,
            'purchase_count_today': self.purchase_count_today
        }


class Incident(Base):
    __tablename__ = 'incidents'
    
    incident_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    incident_type = Column(String(50))
    incident_date = Column(Date, nullable=False)
    location = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    police_report_number = Column(String(50))
    description = Column(Text)
    severity = Column(String(20))
    reported_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='incidents')
    
    def to_dict(self):
        return {
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'incident_type': self.incident_type,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'location': self.location,
            'police_report_number': self.police_report_number,
            'severity': self.severity,
            'reported_by': self.reported_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PatternFlag(Base):
    __tablename__ = 'pattern_flags'
    
    flag_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    pattern_type = Column(String(50))
    detected_date = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    details = Column(JSONB)
    reviewed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='pattern_flags')
    
    def to_dict(self):
        return {
            'flag_id': self.flag_id,
            'user_id': self.user_id,
            'pattern_type': self.pattern_type,
            'detected_date': self.detected_date.isoformat() if self.detected_date else None,
            'confidence_score': self.confidence_score,
            'details': self.details,
            'reviewed': self.reviewed
        }


class Alert(Base):
    __tablename__ = 'alerts'
    
    alert_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    alert_type = Column(String(50))
    message = Column(Text)
    severity = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='alerts')
    
    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged': self.acknowledged
        }