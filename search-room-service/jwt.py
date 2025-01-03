import requests
from flask import request

JWT_VALIDATION_URL = "http://localhost:5005/protected"
USER_PROFILE_URL = "http://localhost:5006/api/profile"
USER_PREFERENCES_URL="http://localhost:5006/api/profile/preferences"

def validate_jwt():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("jwtToken")
        if not token:
            return None, "JWT token is missing from both Authorization header and cookies"

    response = requests.get(JWT_VALIDATION_URL, headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return None, f"JWT Validation Error: {response.status_code}"

    return response.json(), None


def get_user_profile(user_id):
    """Запит до сервісу профілю для отримання даних користувача"""
    response = requests.get(f"{USER_PROFILE_URL}/{user_id}")
    if response.status_code != 200:
        return None, f"Failed to fetch profile: {response.status_code}"
    return response.json(), None


def get_user_preferences(user_id):
    """Запит до сервісу профілю для отримання даних користувача"""
    response = requests.get(f"{USER_PREFERENCES_URL}/{user_id}")
    if response.status_code != 200:
        return None, f"Failed to fetch profile: {response.status_code}"
    return response.json(), None