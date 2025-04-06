from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app.extensions import db, jwt
from app.schemas import UserLogin
from app.utils.helpers import format_error_message
from pydantic import ValidationError
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user_data = UserLogin.model_validate(data)
        user = User.query.filter_by(email=user_data.email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "message": "Token is valid",
        "user": user.to_dict()
    }), 200

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "message": "The token has expired",
        "error": "token_expired"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "message": "Signature verification failed",
        "error": "invalid_token"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "message": "Request does not contain an access token",
        "error": "authorization_required"
    }), 401