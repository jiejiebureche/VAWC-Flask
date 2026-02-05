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

    