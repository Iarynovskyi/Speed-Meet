from flask import Flask, request, jsonify, redirect
from config_profile import Config
from dto_profile.api_input import UserProfileDTO
from business_profile import (
    user_profile,
    add_hobbies_to_profile,
    create_user_preferences,
    get_user_profile_with_hobbies,
    get_user_preferences
)
from database_profile.models.user_profiles import db, Country, Hobby
from jwt import validate_jwt

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/api/profile', methods=['POST'])
def profile_endpoint():
    user_data, error = validate_jwt()
    if error:
        #return redirect("http://localhost:5005/login")
        return jsonify({"error": error}), 401

    username = user_data.get("logged_in_as")
    data = request.get_json()
    dto = UserProfileDTO().load(data)
    user_info = user_profile(username, dto)
    return user_info


@app.route('/api/profile/hobbies', methods=['POST'])
def add_hobbies():
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401

    user_id = user_data.get("logged_in_as")
    data = request.get_json()
    result = add_hobbies_to_profile(user_id, data)
    return result


@app.route('/api/profile/preferences', methods=['POST'])
def create_preferences():
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401

    user_id = user_data.get("logged_in_as")
    data = request.get_json()
    result = create_user_preferences(user_id, data)
    return result


@app.route('/api/profile', methods=['GET'])
def get_profile():
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401

    user_id = user_data.get("logged_in_as")
    profile = get_user_profile_with_hobbies(user_id)
    return profile


@app.route('/api/profile/preferences', methods=['GET'])
def get_preferences():
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401

    user_id = user_data.get("logged_in_as")
    preferences = get_user_preferences(user_id)
    return preferences


@app.route('/api/countries', methods=['GET'])
def get_countries():
    countries = [{"id": c.id, "name": c.name} for c in Country.query.all()]
    return countries


@app.route('/api/hobbies', methods=['GET'])
def get_hobbies():
    hobbies = [{"id": h.id, "name": h.name} for h in Hobby.query.all()]
    return hobbies


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
