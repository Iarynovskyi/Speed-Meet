from flask import Flask, request, jsonify, redirect
from config_search_room import Config
from business_search_room import set_user_online, info_from_service, recommendation_people_for_you
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

    set_user_online(user_id)
    user_data = info_from_service(user_id)
    prof = recommendation_people_for_you(user_id)
    print("Recommend list for you:", prof)

    return jsonify({
        "message": "Allgood",
        "profile": user_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
