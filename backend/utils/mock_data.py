import random
from datetime import datetime, timedelta
from faker import Faker
from models import User, Shop, Transaction, Incident
from database import Session

fake = Faker('en_IN')

class MockDataGenerator:
    """Generate realistic test data"""
    
    @staticmethod
    def generate_users(count=50):
        """Generate mock users"""
        db = Session()
        users = []
        
        for _ in range(count):
            user = User(
                aadhaar_mock=str(random.randint(100000000000, 999999999999)),
                name=fake.name(),
                age=random.randint(18, 75),
                address=fake.address(),
                phone=str(random.randint(6000000000, 9999999999)),
                registration_date=fake.date_time_between(start_date='-2y', end_date='now')
            )
            users.append(user)
        
        db.bulk_save_objects(users)
        db.commit()
        print(f"✅ Generated {count} users")
        db.close()
        return users
    
    @staticmethod
    def generate_shops(count=20):
        """Generate mock TASMAC shops"""
        db = Session()
        
        districts = ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Trichy', 
                     'Tirunelveli', 'Erode', 'Vellore', 'Thanjavur', 'Kanchipuram']
        
        shops = []
        for i in range(count):
            district = random.choice(districts)
            shop = Shop(
                shop_name=f"TASMAC {district} Shop {i+1}",
                location=fake.street_address(),
                district=district,
                pincode=str(random.randint(600001, 643253)),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                license_number=f"TN{random.randint(10000, 99999)}"
            )
            shops.append(shop)
        
        db.bulk_save_objects(shops)
        db.commit()
        print(f"✅ Generated {count} shops")
        db.close()
        return shops
    
    @staticmethod
    def generate_transactions(user_ids, shop_ids, count=500):
        """Generate mock transactions"""
        db = Session()
        
        alcohol_types = [
            {'type': 'Beer', 'brands': ['Kingfisher', 'Tuborg', 'Carlsberg'], 'abv': 5.0, 'price_range': (100, 200)},
            {'type': 'Whiskey', 'brands': ['Royal Stag', 'McDowell', 'Officers Choice'], 'abv': 42.8, 'price_range': (500, 2000)},
            {'type': 'Rum', 'brands': ['Old Monk', 'Bacardi', 'McDowell'], 'abv': 42.8, 'price_range': (400, 1500)},
            {'type': 'Vodka', 'brands': ['Magic Moments', 'Smirnoff', 'Absolut'], 'abv': 40.0, 'price_range': (600, 2500)},
            {'type': 'Brandy', 'brands': ['Mansion House', 'Honey Bee', 'McDowell'], 'abv': 40.0, 'price_range': (400, 1800)}
        ]
        
        transactions = []
        for _ in range(count):
            alcohol = random.choice(alcohol_types)
            quantity_ml = random.choice([180, 375, 750, 1000])
            abv = alcohol['abv']
            units = (quantity_ml * abv) / 1000
            
            transaction = Transaction(
                user_id=random.choice(user_ids),
                shop_id=random.choice(shop_ids),
                transaction_date=fake.date_time_between(start_date='-60d', end_date='now'),
                alcohol_type=alcohol['type'],
                brand=random.choice(alcohol['brands']),
                quantity_ml=quantity_ml,
                units=round(units, 2),
                abv_percentage=abv,
                amount_paid=random.uniform(*alcohol['price_range']),
                payment_method=random.choice(['Cash', 'Card', 'UPI']),
                latitude=fake.latitude(),
                longitude=fake.longitude()
            )
            transactions.append(transaction)
        
        db.bulk_save_objects(transactions)
        db.commit()
        print(f"✅ Generated {count} transactions")
        db.close()
    
    @staticmethod
    def generate_incidents(user_ids, count=20):
        """Generate mock incidents"""
        db = Session()
        
        incident_types = ['Violence', 'DUI', 'Public Disturbance', 'Domestic Violence', 'Assault']
        severities = ['Low', 'Medium', 'High']
        
        incidents = []
        for _ in range(count):
            incident = Incident(
                user_id=random.choice(user_ids),
                incident_type=random.choice(incident_types),
                incident_date=fake.date_between(start_date='-1y', end_date='today'),
                location=fake.address(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                police_report_number=f"FIR{random.randint(1000, 9999)}/2024",
                description=fake.sentence(),
                severity=random.choice(severities),
                reported_by=random.choice(['Police', 'Shop Manager', 'Public'])
            )
            incidents.append(incident)
        
        db.bulk_save_objects(incidents)
        db.commit()
        print(f"✅ Generated {count} incidents")
        db.close()
    
    @staticmethod
    def generate_all_data():
        """Generate complete mock dataset"""
        print("🚀 Starting mock data generation...")
        
        # Generate users
        MockDataGenerator.generate_users(50)
        
        # Get user IDs
        db = Session()
        user_ids = [u.user_id for u in db.query(User).all()]
        
        # Generate shops
        MockDataGenerator.generate_shops(20)
        shop_ids = [s.shop_id for s in db.query(Shop).all()]
        db.close()
        
        # Generate transactions
        MockDataGenerator.generate_transactions(user_ids, shop_ids, 500)
        
        # Generate incidents
        MockDataGenerator.generate_incidents(user_ids, 20)
        
        print("✅ Mock data generation complete!")