from flask import Blueprint, request, jsonify, url_for, abort
from app.models.user import User
from app import db
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def users():
    users = User.query.all()
    
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.filter_by(id=id).first()
    
    if user is None:
        abort(404, description=f"User ID {id} not found")
        
    safe_user = {"id": user.id, "name": user.name, "dob": user.dob, "barangay_complainant": user.barangay_complainant, "city": user.city, "role": user.role, "contact_num": user.contact_num}
    
    return jsonify(safe_user), 200
