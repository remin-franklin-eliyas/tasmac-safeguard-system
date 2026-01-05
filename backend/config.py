import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Business Rules
    DAILY_UNIT_LIMIT = float(os.getenv('DAILY_UNIT_LIMIT', 40))
    MAX_PURCHASES_PER_DAY = int(os.getenv('MAX_PURCHASES_PER_DAY', 3))
    
    # Risk Scoring Thresholds
    RISK_THRESHOLD_YELLOW = 40
    RISK_THRESHOLD_RED = 70
    
    # Pattern Detection
    BULK_PURCHASE_THRESHOLD_ML = 1000
    HIGH_FREQUENCY_THRESHOLD = 20