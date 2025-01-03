from flask import Flask, request, jsonify, redirect
from config_search_room import Config
from dto_profile.api_input import UserProfileDTO
from business_search_room import (
    recommendation_people_for_you
)
from database_profile.models.user_profiles import db, Country, Hobby
from jwt import validate_jwt, get_user_profile, get_user_preferences

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/api/find_room', methods=['GET'])
def find_room():
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401
    user_id = user_data.get("logged_in_as")

    profile, error = get_user_profile(user_id)
    if error:
        return jsonify({"error": error}), 500

    preferences, error = get_user_preferences(user_id)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "message": "Allgood",
        "profile": profile,
        "preferences": preferences
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
