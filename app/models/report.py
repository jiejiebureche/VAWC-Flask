from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_name = db.Column(db.String(255), nullable=False)
    
    reporter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    reporter = db.relationship('User', backref=db.backref('reports', lazy=True))
    
    city = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complainant_brgy = db.Column(db.String(100), nullable=False)
    incident_brgy = db.Column(db.String(100), nullable=False)
    reporter_type = db.Column(db.Enum('victim', 'witness', name='reporter_types'), nullable=False)
    incident_type = db.Column(db.Enum('Physical Abuse', 'Verbal Abuse', 'Sexual Harassment', 'Child Abuse', name='incident_types'), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('unopened', 'viewed', 'pending', 'resolved', name='report_status'), nullable=False, default='unopened')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    evidences = db.Column(JSONB)

    def __repr__(self):
        return f'<Report {self.id} - {self.status}>'

    @staticmethod
    def create_report(**kwargs):
        
        required_fields = ["reporter_name", "reporter_id", "city", "description", "complainant_brgy", 
                    "incident_brgy", "reporter_type", "incident_type", "location"]
        
        allowed_optional = ['status', 'evidences']
        
        for field in required_fields:
            if not kwargs.get(field):
                raise ValueError(f"The field '{field}' is mandatory.")
        
        all_allowed = required_fields + allowed_optional
        
        for param in kwargs.keys():
            if param not in all_allowed:
                raise ValueError(f"The field '{param}' is not allowed.") 
            
        # Ensure evidences is at least an empty list for JSONB consistency
        evidences = kwargs.pop('evidences', [])

        new_report = Report(
            evidences=evidences,
            **kwargs
        )
        
        try:
            db.session.add(new_report)
            db.session.commit()
            return new_report
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        return {
            "id": str(self.id), 
            "reporter_name": self.reporter_name,
            "reporter_id": str(self.reporter_id),  
            "city": self.city,
            "description": self.description,
            "complainant_brgy": self.complainant_brgy,
            "incident_brgy": self.incident_brgy,
            "reporter_type": self.reporter_type,
            "incident_type": self.incident_type,
            "location": self.location,
            "status": self.status,
            "evidences": self.evidences,  
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }   