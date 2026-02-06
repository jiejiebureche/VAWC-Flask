from datetime import datetime
from app import db, bcrypt  # Using your initialized instances
from sqlalchemy.orm import validates
import re
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    barangay_complainant = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.String(13), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'agent', name='user_roles'), nullable=False, default='user')
    id_type = db.Column(db.String(50), default='image', nullable=False)
    id_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        # This will trigger the @validates('password') method below
        self.validate_password('password', password)
        # If validation passes, hash it and store it
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    # --- PH Contact Number Validation ---
    @validates('contact_num')
    def validate_contact_num(self, key, number):
        # Regex for PH numbers (supports +63 or 09)
        ph_regex = r"^(09|\+639)\d{9}$"
        if not re.match(ph_regex, number) or len(number) > 13:
            raise ValueError("Contact number is not valid for the Philippines!")
        return number

    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address
    
    @validates('password')
    def validate_password(self, key, password):
        
        special_chars_regex = r'.*[!@#$%^&*()_+\-=\[\]{};:\'"|\\,./<>?]'
        
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            raise ValueError('Password must contain at least one number.')
        if not re.search(special_chars_regex, password):
            raise ValueError('Password must contain at least one special character.')
    
    def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "dob": self.dob,
                "complainant_brgy": self.barangay_complainant,
                "contact_num": self.contact_num,
                "email": self.email,
                "city": self.city,
                "role": self.role,
                "created_at": self.created_at.isoformat() # Dates must be converted to strings
            }
             
    def generate_activation_token(self, email=None, purpose='activate'):
        email_to_encode = email if email else self.email
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps({'user_id': str(self.id), 'new_email': email_to_encode, "purpose": purpose}, salt='email-confirm')
    
    @staticmethod
    def create_inactive_user(name, dob, city, barangay, contact_num, email, is_active, password, id_url, role='user'):
        if not email or not password:
            raise ValueError("All fields must be filled!")

        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")
        

        new_user = User(
            name=name,
            dob=dob,
            city=city,
            barangay_complainant=barangay,
            contact_num=contact_num,
            email=email,
            is_active=is_active,
            id_url=id_url,
            role=role
        )
            
        new_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db.session.add(new_user)
        db.session.commit()
        return new_user
            
    @staticmethod
    def login(email, password):
        if not email or not password:
            raise ValueError("All fields must be filled!")

        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("Incorrect email address")

        if not bcrypt.check_password_hash(user.password_hash, password):
            raise ValueError("Incorrect password")

        return user
    
    