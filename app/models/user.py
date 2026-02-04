from datetime import datetime
from app import db, bcrypt  # Using your initialized instances
from sqlalchemy.orm import validates
import re

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    barangay_complainant = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.String(13), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'agent', name='user_roles'), nullable=False, default='user')
    id_type = db.Column(db.String(50), default='image')
    id_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- PH Contact Number Validation ---
    @validates('contact_num')
    def validate_contact_num(self, key, number):
        # Regex for PH numbers (supports +63 or 09)
        ph_regex = r"^(09|\+639)\d{9}$"
        if not re.match(ph_regex, number) or len(number) > 13:
            raise ValueError("Contact number is not valid for the Philippines!")
        return number

    @staticmethod
    def signup(name, dob, city, barangay, contact_num, password, id_url, role='user'):
        if not contact_num or not password:
            raise ValueError("All fields must be filled!")

        if User.query.filter_by(contact_num=contact_num).first():
            raise ValueError("Contact number already registered")

        new_user = User(
            name=name,
            dob=dob,
            city=city,
            barangay_complainant=barangay,
            contact_num=contact_num,
            id_url=id_url,
            role=role
        )
        
        new_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login(contact_num, password):
        if not contact_num or not password:
            raise ValueError("All fields must be filled!")

        user = User.query.filter_by(contact_num=contact_num).first()
        if not user:
            raise ValueError("Incorrect contact number")

        if not bcrypt.check_password_hash(user.password_hash, password):
            raise ValueError("Incorrect password")

        return user