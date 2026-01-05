import re
from datetime import datetime

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_aadhaar(aadhaar):
        """Validate Aadhaar format (12 digits)"""
        if not aadhaar or not isinstance(aadhaar, str):
            return False, "Aadhaar is required"
        
        if not re.match(r'^\d{12}$', aadhaar):
            return False, "Aadhaar must be exactly 12 digits"
        
        return True, None
    
    @staticmethod
    def validate_age(age):
        """Validate age (must be 18+)"""
        if not age or not isinstance(age, int):
            return False, "Age is required and must be a number"
        
        if age < 18:
            return False, "User must be at least 18 years old"
        
        if age > 120:
            return False, "Invalid age"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (10 digits)"""
        if not phone:
            return True, None  # Phone is optional
        
        if not re.match(r'^\d{10}$', phone):
            return False, "Phone number must be exactly 10 digits"
        
        return True, None
    
    @staticmethod
    def validate_units(units):
        """Validate alcohol units"""
        if units is None or not isinstance(units, (int, float)):
            return False, "Units must be a number"
        
        if units <= 0:
            return False, "Units must be greater than 0"
        
        if units > 50:
            return False, "Units too high for single transaction"
        
        return True, None
    
    @staticmethod
    def validate_quantity(quantity_ml):
        """Validate quantity in ml"""
        if quantity_ml is None or not isinstance(quantity_ml, int):
            return False, "Quantity must be a number"
        
        if quantity_ml <= 0:
            return False, "Quantity must be greater than 0"
        
        if quantity_ml > 10000:
            return False, "Quantity too high for single transaction"
        
        return True, None
    
    @staticmethod
    def calculate_units(quantity_ml, abv_percentage):
        """
        Calculate standard drink units
        Formula: (volume_ml × ABV%) / 1000 = units
        (10ml of pure alcohol = 1 unit)
        """
        if not quantity_ml or not abv_percentage:
            return 0
        
        return (quantity_ml * abv_percentage) / 1000