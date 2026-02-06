from flask import Blueprint, request, jsonify, url_for, abort
from app.models.user import User
from app import db, bcrypt, mail
from flask_mail import Message
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

#Get all users
@user_bp.route('/', methods=['GET'])
@jwt_required()
def users():
    users = User.query.all()
    
    return jsonify([user.to_dict() for user in users]), 200

#Get user by ID
@user_bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.filter_by(id=id).first()
    
    if user is None:
        abort(404, description=f"User ID {id} not found")
        
    safe_user = {"id": user.id, "name": user.name, "dob": user.dob, "barangay_complainant": user.barangay_complainant, "city": user.city, "role": user.role, "contact_num": user.contact_num}
    
    return jsonify(safe_user), 200

#Update user info by ID
@user_bp.route('/<uuid:id>', methods=['PATCH'])
@jwt_required()
def update_user_info(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)

    # Security: Only owner can edit
    if current_user_id != str(user.id):
        return jsonify({"message": "Forbidden"}), 403
        
    data = request.get_json()
    allowed_fields = ['name', 'city', 'barangay_complainant', 'contact_num']

    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"message": f"Updating {key} field illegal."}), 403
        setattr(user, key, value)
        
    try:
        db.session.commit()
        return jsonify({
            'message': 'User info updated successfully', 
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 400
    
#Change user password
@user_bp.route('/change-password/<uuid:id>', methods=['PATCH'])
@jwt_required()
def change_password(id):
    
    current_user_id = get_jwt_identity()
    if current_user_id != str(id):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"message": "Both current and new passwords are required"}), 400

    user = User.query.get_or_404(id)

    if not bcrypt.check_password_hash(user.password_hash, current_password):
        return jsonify({"message": "Incorrect current password"}), 401

    try:
        user.password = new_password
        db.session.commit()
        
        return jsonify({
            "message": "Change Password Successful"
        }), 200
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'message': 'Validation failed', 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

#Change email route
@user_bp.route('/change-email/<uuid:id>', methods=['PATCH'])
@jwt_required()
def change_email(id):
    current_user_id = get_jwt_identity()
    
    if current_user_id != str(id):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    new_email = data.get('new_email')
    
    if not new_email:
        return jsonify({"message": "Email field is required!"}), 400
    
    user = User.query.get_or_404(id)
    
    if user.email == new_email:
        return jsonify({"message": "Current email can't be used as New email"}), 400
    
    try:
        token = user.generate_activation_token(email=new_email, purpose='change-email')

        activation_link = f"http://localhost:5555/auth/activate/{token}"

        # 4. Send Email via Mailtrap
        msg = Message(
            'Activate Your VAWC DeskHub Account',
            sender='noreply@vawc-deskhub.com',
            recipients=[new_email]
        )
        msg.body = f"Hello {user.name},\n\nPlease click the link below to activate your account:\n{activation_link}"
        mail.send(msg)
        
        return jsonify({"message": "Registration successful. Please check your email to activate your account."}), 201
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An error occurred during registration.",
            "details": str(e) 
        }), 500    

#Delete user by id route
@user_bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    
    if user is None:
        abort(404, description=f"User ID {id} not found")
        
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User successfully deleted"}), 204
    
    
    
    
    
    
    
        
    
