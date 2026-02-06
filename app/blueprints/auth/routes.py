from flask import Blueprint, request, jsonify, url_for
from app.models.user import User
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password=data.get('password')
    
    try:
        user = User.login(email, password)
        
        if not user.is_active:
            return jsonify({"error": "Account not activated. Please check your email."}), 403
        
        access_token = create_access_token(identity=str(user.id))
        
        safe_user = {"id": user.id, "name": user.name, "dob": user.dob, "barangay_complainant": user.barangay_complainant, "city": user.city, "role": user.role, "contact_num": user.contact_num}
        
        return jsonify({"message": "Login successful.", "access_token": access_token, "user": safe_user}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({
            "error": "An error occurred during login.",
            "details": str(e) 
        }), 500

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    try:
        # 1. Create the user in the database (is_active=False)
        user = User.create_inactive_user(
            name=data.get('name'),
            dob=data.get('dob'),
            city=data.get('city'),
            barangay=data.get('barangay_complainant'),
            contact_num=data.get('contact_num'),
            email=data.get('email'),
            is_active=False,
            password=data.get('password'),
            id_url=data.get('id_url'),
            role=data.get('role', 'user')
        )

        # 2. Generate Activation Token
        token = user.generate_activation_token()
        
        # 3. Create Activation Link
        # In production, this would point to your React Frontend URL
        activation_link = f"http://localhost:5555/auth/activate/{token}"

        # 4. Send Email via Mailtrap
        msg = Message(
            'Activate Your VAWC DeskHub Account',
            sender='noreply@vawc-deskhub.com',
            recipients=[user.email]
        )
        msg.body = f"Hello {user.name},\n\nPlease click the link below to activate your account:\n{activation_link}"
        mail.send(msg)

        return jsonify({"message": "Registration successful. Please check your email to activate your account."}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # This will now tell you EXACTLY what failed (e.g., Mail configuration or Token error)
        return jsonify({
            "error": "An error occurred during registration.",
            "details": str(e) 
        }), 500

@auth_bp.route('/activate/<token>', methods=['GET'])
def activate(token):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    
    try:
        data = serializer.loads(token, salt='email-confirm', max_age=3600)
        
        new_email = data.get('new_email')
        purpose = data.get('purpose')
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found."}), 404

        if purpose == 'activate':
            if user.is_active:
                return jsonify({"message": "Account already activated."}), 200
            user.is_active = True
        
        elif purpose == 'change-email':
            user.email = new_email

        elif purpose not in ['activate', 'change-email']:
            return jsonify({"message": "Invalid purpose"}), 400

        db.session.commit()
        
        return jsonify({"message": "Account activated successfully! You can now log in."}), 200
    
    except Exception:
        db.session.rollback()
        return jsonify({"error": "The activation link is invalid or has expired."}), 400
