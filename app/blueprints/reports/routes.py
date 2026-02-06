from flask import Blueprint, request, jsonify, url_for, abort
from app.models.report import Report
from app.models.user import User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    reports = Report.query.all()
    
    return jsonify([report.to_dict() for report in reports])

@reports_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_report_by_id(id):
    report = Report.query.get(id)
    
    if report is None:
        abort(404, description=f"User ID {id} not found")
    
    return jsonify(report.to_dict())

@reports_bp.route('/create-report', methods=['POST'])
@jwt_required()
def create_report():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if data is None:
        return jsonify({"message": "Create report body cannot be empty"}), 400
    
    user = User.query.get_or_404(current_user_id)
    reporter_name = user.name
    reporter_id = user.id
    complainant_brgy = user.barangay_complainant
    
    if user.role != 'user':
        return jsonify({"message": "Only users are allowed to create a report"}), 403
    
    try:
        report = Report.create_report(
            reporter_name=reporter_name,
            reporter_id=reporter_id,
            complainant_brgy=complainant_brgy,
            **data
        )
        
        db.session.commit()
        return jsonify({"message": f"Report Successfully Created", "report": report.to_dict()}), 201
    except ValueError as e:
        # Catches missing fields or validation failures
        return jsonify({"error": "Validation Error", "details": str(e)}), 400

    except Exception as e:
        # The "Safety Net" for everything else
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
    
@reports_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_report(id):
    data = request.get_json()
    report = Report.query.get(id)
    
    allowed_fields = ["reporter_name", "city", "description", "incident_brgy", "reporter_type", "incident_type", "location", "evidences"]
        
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"message": f"You are not allowed to update the {key} field"}), 200
        setattr(report, key, value)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Report info updated successfully', 
            'user': report.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 400
    