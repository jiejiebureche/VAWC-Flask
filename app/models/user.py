from datetime import datetime
from sqlalchemy.orm import validates
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    city = db.Column(db.String, nullable=False)
    complainant_brgy = db.Column(db.String, nullable=False)
    contact_num = db.Column(db.Integer, nullable=False) 
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'agent', name='user_roles'), nullable=False, default='user')
    id_type = db.Column(db.String(50), default='image') # e.g., "passport", "drivers_license"
    id_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"User: {self.name}"
    
    @validates(password)
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return password