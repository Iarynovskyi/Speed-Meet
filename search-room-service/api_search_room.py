import time

from flask import Flask, request, jsonify, redirect
from config_search_room import Config
from business_search_room import (
    set_user_online, info_from_service,
    recommendation_people_for_you,
    create_room_with_waiting,
    now_you_can_read_a_little_about_your_partner,
    create_vip_room,
    leave_room
)
from database_search_room.models.search_room import db
from jwt import validate_jwt
import asyncio
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

@app.route('/api/find_room', methods=['GET'])
def find_room():
    start_time = time.time()
    user_data, error = validate_jwt()
    if error:
        return jsonify({"error": error}), 401
    user_id = user_data.get("logged_in_as")

    set_user_online(user_id)
    user_data = info_from_service(user_id)

    start_time2 = time.time()

    prof = asyncio.run(create_room_with_waiting(user_id, user_data))
    end_time2 = time.time()  # час завершення
    print("Recommend list for you:", prof)
    now_you_can_read_a_little_about_your_partner(prof["partner"], prof["profile"])

    end_time = time.time()  # час завершення
    execution_time = end_time - start_time
    execution_time2 = end_time2 - start_time2

    print(f"Час виконання: {execution_time} секунд")
    print(f"Час виконання: {execution_time2} секунд")

    return jsonify({
        "message": "Allgood",
        "profile": user_data
    })

@app.route('/api/vip_room', methods=['POST'])
def vip_room():
    data = request.json
    user_1_id = data.get('user_1_id')
    user_2_id = data.get('user_2_id')
    create_vip_room(user_1_id, user_2_id)
    return {"msg": "Allgood"}


@app.route('/api/leave_room', methods=['POST'])
def leave_room():
    data = request.json
    user_1_id = data.get('user_1_id')
    user_2_id = data.get('user_2_id')
    leave_room(user_1_id, user_2_id)
    return {"msg": "Allgood"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
