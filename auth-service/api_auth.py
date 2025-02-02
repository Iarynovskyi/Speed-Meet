'''
Створення основної апі частини проєкту з урахування конфігурацій проєкту
'''


from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config_auth import Config
from dto_auth.api_input import UserDTO
from business_auth import check_user_register, check_user_login, token_required
from database_auth.models.users import db
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
db.init_app(app)
CORS(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    dto = UserDTO().load(data)
    result = check_user_register(dto)
    return result

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    dto = UserDTO().load(data)
    result = check_user_login(dto)
    return result


@app.route('/protected', methods=['GET'])
#@jwt_required(refresh=True)
@token_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
