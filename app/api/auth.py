from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app.extensions import db, jwt
from app.schemas import UserLogin
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
        
        # Create the JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
    except ValidationError as e:
        errors = []
        for error in e.errors():
            error_location = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": error_location,
                "message": error["msg"]
            })
        
        return jsonify({
            "message": "Validation error",
            "errors": errors
        }), 400


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify a token is valid and return user info"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "message": "Token is valid",
        "user": user.to_dict()
    }), 200


# JWT error handlers
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