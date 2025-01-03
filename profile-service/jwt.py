import requests
from flask import request

JWT_VALIDATION_URL = "http://localhost:5005/protected"

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
