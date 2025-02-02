from functools import wraps

import jwt
from config_auth import Config
from database_auth.models.users import User
from flask import jsonify, make_response, request
from flask_jwt_extended import  create_access_token


def check_user_register(dto: dict):
    if User.get_user_by_username(dto.get('email'), dto.get('username')):
        return jsonify({"msg": "User already exists"}), 400

    user = User.add_user(dto.get('username'), dto.get('password'), dto.get('email'))
    return jsonify({"msg": f"User {dto.get('username')} registered successfully"}), 201


def check_user_login(dto: dict):
    user = User.get_user_by_username(dto.get('email'), dto.get('username'))

    if user and user.check_password(dto.get('password')):
        access_token = create_access_token(identity=user.username)
        response = make_response({"message": "Login successful",
                                  "access_token": access_token,
                                  "user": user.username})
        response.set_cookie(
            "jwtToken",
            access_token,
            httponly=True,
            secure=True,  # Використовуйте secure=True у production для HTTPS
            samesite='Strict'  # Запобігає відправці з сторонніх сайтів
        )
        return response
        # return jsonify(access_token=access_token,
        #                user=user.username), 200

    return jsonify({"msg": "Invalid credentials"}), 401


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Перевірка чи токен є в cookie
        if 'token' in request.cookies:
            token = request.cookies['token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Декодування токену
            decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403

        return f(current_user, *args, **kwargs)

    return decorated_function