from database_auth.models.users import User
from flask import jsonify, make_response
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
        # response = make_response({"message": "Login successful"})
        # response.set_cookie(
        #     "jwtToken",
        #     access_token,
        #     httponly=True,
        #     secure=True,  # Використовуйте secure=True у production для HTTPS
        #     samesite='Strict'  # Запобігає відправці з сторонніх сайтів
        # )
        # return response
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid credentials"}), 401