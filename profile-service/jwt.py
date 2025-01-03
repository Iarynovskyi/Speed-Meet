import requests
from flask import request

JWT_VALIDATION_URL = "http://localhost:5005/protected"

def validate_jwt():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Authorization header is missing or invalid"

    token = auth_header.split(" ")[1]

    response = requests.get(JWT_VALIDATION_URL, headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return None, f"JWT Validation Error: {response.status_code}"

    return response.json(), None
